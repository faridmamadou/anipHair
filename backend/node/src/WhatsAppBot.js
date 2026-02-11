const { default: makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');
const path = require('path');

const { handleConnection } = require('./handlers/connectionHandler');
const { handleAudioMessage } = require('./handlers/audioHandler');
const { unwrapMessage, extractMessageContent } = require('./handlers/messageHandler');
const apiService = require('./services/apiService');
const { parseContactList, extractPhoneFromJid } = require('./utils/phoneUtils');
const { sleep, markAsRead, sendTyping } = require('./utils/botUtils');

class WhatsAppBot {
    constructor() {
        this.sock = null;
        this.logger = pino({ level: 'silent' });

        // Configuration of allowed/excluded contacts
        this.setupContactFilters();
    }

    setupContactFilters() {
        const includedOnlyEnv = process.env.INCLUDED_ONLY || '';
        const excludedEnv = process.env.EXCLUDED || '';

        this.includedOnly = parseContactList(includedOnlyEnv);
        this.excluded = parseContactList(excludedEnv);

        console.log('🔧 Contact filters configuration:');
        console.log(`📞 Only authorized contacts: ${this.includedOnly.length > 0 ? this.includedOnly.join(', ') : 'All authorized'}`);
        console.log(`🚫 Excluded contacts: ${this.excluded.length > 0 ? this.excluded.join(', ') : 'None excluded'}`);
    }

    isContactAllowed(jid, isGroup = false) {
        const phoneNumber = extractPhoneFromJid(jid);

        if (this.excluded.length > 0) {
            const isExcluded = this.excluded.some(excludedNumber =>
                phoneNumber.includes(excludedNumber) || excludedNumber.includes(phoneNumber)
            );
            if (isExcluded) {
                console.log(`🚫 Excluded contact: ${phoneNumber}`);
                return false;
            }
        }

        if (this.includedOnly.length > 0) {
            const isIncluded = this.includedOnly.some(includedNumber =>
                phoneNumber.includes(includedNumber) || includedNumber.includes(phoneNumber)
            );
            if (!isIncluded) {
                console.log(`📵 Unauthorized contact: ${phoneNumber}`);
                return false;
            }
        }

        console.log(`✅ Authorized contact: ${phoneNumber}`);
        return true;
    }

    async startBot() {
        const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');

        this.sock = makeWASocket({
            auth: state,
            logger: this.logger,
            browser: ['Ubuntu', 'Chrome', '110.0.5481.177'],
            defaultQueryTimeoutMs: 60000
        });

        this.sock.ev.on('creds.update', saveCreds);
        this.sock.ev.on('connection.update', (update) => handleConnection(update, this.startBot.bind(this)));
        this.sock.ev.on('messages.upsert', this.handleMessages.bind(this));
    }



    async handleMessages(m) {
        const msg = m.messages[0];
        if (!msg.message) return;

        const from = msg.key.remoteJid;
        const senderName = msg.pushName || 'User';
        const isGroup = from.endsWith('@g.us');
        const participantId = msg.key.participant || msg.participant;

        // Ignorer les statuts WhatsApp et broadcasts
        if (from === 'status@broadcast' || from.includes('broadcast')) {
            return;
        }

        const contactToCheck = isGroup ? participantId : from;
        if (!this.isContactAllowed(contactToCheck, isGroup)) {
            console.log(`🔒 Message ignored - Unauthorized contact`);
            return;
        }

        await markAsRead(this.sock, msg.key);

        const message = unwrapMessage(msg.message);
        let messageContent = null;
        let audioInfo = null;
        let type = '';

        if (message?.audioMessage) {
            console.log(`🎵 Audio message received from ${senderName} (${from})`);
            audioInfo = await handleAudioMessage(this.sock, msg, from, senderName, this.logger);
            if (audioInfo) {
                type = 'audio';
                console.log(`🎵 Audio buffer saved`);
            } else {
                messageContent = '[Audio message - download failed]';
            }
        } else {
            messageContent = extractMessageContent(msg);
            type = 'text';
        }

        console.log(`📨 Message from ${senderName} (${from}): ${messageContent || '[Audio]'}`);

        const shouldRespond = !isGroup || (messageContent && messageContent.startsWith('/')) || audioInfo;

        if (!shouldRespond) {
            console.log(`🔇 Message ignored (group without mention)`);
            return;
        }

        await sleep(10);

        try {
            await sendTyping(this.sock, from);

            // Forward to FastAPI
            const content = audioInfo ? audioInfo : messageContent;

            if (content) {
                const response = await apiService.sendMessage({
                    type,
                    content,
                    senderId: from,
                    mimetype: audioInfo?.mimetype
                });

                console.log(`🚀 Message forwarded to FastAPI (${type})`);

                // Handle direct reply from FastAPI
                if (response && response.received && response.reply) {
                    await this.sendMessage(from, response.reply);
                } else if (response && response.reply) {
                    await this.sendMessage(from, response.reply);
                }
            }

        } catch (error) {
            console.error('❌ Error during processing:', error);
        }
    }

    async sendMessage(to, message) {
        try {
            await this.sock.sendMessage(to, { text: message });
            console.log(`📤 Message sent to ${to}: ${message}`);
        } catch (error) {
            console.error('❌ Error sending message:', error);
        }
    }

    async sendMessageWithMention(to, message, mentionJid, mentionName, quotedMessage) {
        try {
            const tag = `@${mentionJid.split('@')[0]}`;
            const fullMessage = `${tag} ${message}`;

            await this.sock.sendMessage(to, {
                text: fullMessage,
                mentions: [mentionJid]
            }, {
                quoted: quotedMessage
            });

            console.log(`📤 Message with mention sent to ${to}: ${fullMessage}`);
        } catch (error) {
            console.error('❌ Error sending message with mention:', error);
            await this.sendMessage(to, `${mentionName}: ${message}`);
        }
    }
}

module.exports = WhatsAppBot;
