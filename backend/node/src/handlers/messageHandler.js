/**
 * Unwraps message content from common containers (ephemeral, viewOnce)
 * @param {object} message - The message object
 * @returns {object} Unwrapped message
 */
function unwrapMessage(message) {
    if (!message) return null;

    if (message.ephemeralMessage) {
        return unwrapMessage(message.ephemeralMessage.message);
    }
    if (message.viewOnceMessage) {
        return unwrapMessage(message.viewOnceMessage.message);
    }
    if (message.viewOnceMessageV2) {
        return unwrapMessage(message.viewOnceMessageV2.message);
    }
    if (message.viewOnceMessageV2Extension) {
        return unwrapMessage(message.viewOnceMessageV2Extension.message);
    }

    return message;
}

/**
 * Extracts text content from a WhatsApp message
 * @param {object} msg - The message object
 * @returns {string} Extracted text
 */
function extractMessageContent(msg) {
    const message = unwrapMessage(msg.message);
    if (!message) return '';

    if (message.conversation) {
        return message.conversation;
    } else if (message.extendedTextMessage) {
        return message.extendedTextMessage.text;
    }
    return '';
}

/**
 * Checks if the bot is mentioned in a group message
 * @param {object} sock - WhatsApp socket instance
 * @param {object} msg - The message object
 * @param {boolean} isGroup - Whether it's a group message
 * @returns {boolean} True if mentioned
 */
async function isBotMentioned(sock, msg, isGroup) {
    if (!isGroup) return false;

    try {
        // Get bot ID
        const botId = sock.user.id;
        const botNumber = botId.split(':')[0];

        // Check mentions in message
        const message = unwrapMessage(msg.message);
        const mentions = message?.extendedTextMessage?.contextInfo?.mentionedJid || [];

        // Check if bot is in mentions
        const isMentioned = mentions.some(mention =>
            mention.includes(botNumber) || mention.includes(botId)
        );

        return isMentioned;
    } catch (error) {
        console.error('❌ Error checking mention:', error);
        return false;
    }
}

module.exports = {
    unwrapMessage,
    extractMessageContent,
    isBotMentioned
};
