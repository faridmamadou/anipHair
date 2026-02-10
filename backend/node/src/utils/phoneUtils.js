/**
 * Phone number utility functions
 */

/**
 * Normalizes a phone number by removing non-numeric characters and handling + prefix
 * @param {string} phoneNumber 
 * @returns {string} Normalized phone number
 */
function normalizePhoneNumber(phoneNumber) {
    if (!phoneNumber) return '';

    // Remove all non-numeric characters except +
    let normalized = phoneNumber.replace(/[^\d+]/g, '');

    // If the number starts with +, keep it
    if (normalized.startsWith('+')) {
        return normalized;
    }

    // If the number starts with 00, replace with +
    if (normalized.startsWith('00')) {
        return '+' + normalized.substring(2);
    }

    return normalized;
}

/**
 * Extracts phone number from a WhatsApp JID
 * @param {string} jid 
 * @returns {string} Normalized phone number
 */
function extractPhoneFromJid(jid) {
    if (!jid) return '';
    // Extract phone number from WhatsApp JID
    // Format: number@s.whatsapp.net or number@g.us (for groups)
    const phoneNumber = jid.split('@')[0];
    return normalizePhoneNumber(phoneNumber);
}

/**
 * Parses a comma-separated list of contact numbers
 * @param {string} contactString 
 * @returns {string[]} Array of normalized phone numbers
 */
function parseContactList(contactString) {
    if (!contactString || contactString.trim() === '') {
        return [];
    }

    return contactString
        .split(',')
        .map(contact => contact.trim())
        .filter(contact => contact !== '')
        .map(contact => normalizePhoneNumber(contact));
}

module.exports = {
    normalizePhoneNumber,
    extractPhoneFromJid,
    parseContactList
};
