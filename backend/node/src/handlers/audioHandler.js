const { downloadMediaMessage } = require('@whiskeysockets/baileys');
const fs = require('fs');
const path = require('path');
const { extractPhoneFromJid } = require('../utils/phoneUtils');
const { unwrapMessage } = require('./messageHandler');

/**
 * Handles incoming audio messages
 * @param {object} sock - WhatsApp socket instance
 * @param {object} messageObj - The full message object
 * @param {string} from - Remote JID
 * @param {string} senderName - Sender's name
 * @param {string} audioDir - Directory to save audio files
 * @param {object} logger - Pino logger instance
 * @returns {Promise<object|null>} Audio information or null if failed
 */
async function handleAudioMessage(sock, messageObj, from, senderName, audioDir, logger) {
    try {
        const message = unwrapMessage(messageObj.message);
        const audioMsg = message?.audioMessage;

        if (!audioMsg) return null;

        console.log('🎵 Audio information:', {
            duration: audioMsg.seconds,
            mimetype: audioMsg.mimetype,
            fileLength: audioMsg.fileLength,
            ptt: audioMsg.ptt // true if it's a voice message
        });

        const downloadOptions = {
            logger: logger,
            reuploadRequest: sock.updateMediaMessage,
            timeoutMs: 60000,
        }

        // Download audio
        const buffer = await downloadMediaMessage(
            messageObj,
            'buffer',
            {},
            downloadOptions
        );

        // Determine extension based on mimetype
        let ext = 'audio';
        if (audioMsg.mimetype) {
            if (audioMsg.mimetype.includes('ogg')) ext = 'ogg';
            else if (audioMsg.mimetype.includes('mpeg')) ext = 'mp3';
            else if (audioMsg.mimetype.includes('mp4')) ext = 'm4a';
            else if (audioMsg.mimetype.includes('wav')) ext = 'wav';
        }

        // Create unique filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const senderPhone = extractPhoneFromJid(from);
        const prefix = audioMsg.ptt ? 'voice' : 'audio';
        const filename = `${prefix}_${senderPhone}_${timestamp}.${ext}`;
        const filepath = path.join(audioDir, filename);

        // Save file
        fs.writeFileSync(filepath, buffer);

        // Return audio file information
        return {
            filename: filename,
            filepath: filepath,
            duration: audioMsg.seconds,
            size: audioMsg.fileLength,
            mimetype: audioMsg.mimetype,
            isVoiceNote: audioMsg.ptt,
            sender: senderName,
            senderPhone: senderPhone,
            timestamp: timestamp
        };

    } catch (error) {
        console.error('❌ Error processing audio:', error);
        return null;
    }
}

module.exports = {
    handleAudioMessage
};
