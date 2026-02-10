/**
 * Bot utility functions
 */

/**
 * Simulates a delay
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Marks a message as read
 * @param {object} sock - WhatsApp socket instance
 * @param {object} messageKey - The key of the message to mark as read
 */
async function markAsRead(sock, messageKey) {
    try {
        await sock.readMessages([messageKey]);
        console.log(`✅ Message marked as read`);
    } catch (error) {
        console.error('❌ Error marking message as read:', error);
    }
}

/**
 * Sends a typing indicator to a contact
 * @param {object} sock - WhatsApp socket instance
 * @param {string} jid - Remote JID
 * @param {number} duration - Duration in milliseconds
 */
async function sendTyping(sock, jid, duration = 2000) {
    try {
        await sock.sendPresenceUpdate('composing', jid);
        // Stop indicator after specified duration
        setTimeout(async () => {
            await sock.sendPresenceUpdate('paused', jid);
        }, duration);
    } catch (error) {
        console.error('❌ Error typing indicator:', error);
    }
}

module.exports = {
    sleep,
    markAsRead,
    sendTyping
};
