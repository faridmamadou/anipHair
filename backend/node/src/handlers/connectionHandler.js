const { DisconnectReason } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const QRCode = require('qrcode');
const path = require('path');

/**
 * Handles connection updates from Baileys
 * @param {object} update - The connection update object
 * @param {function} startBot - Function to restart the bot
 */
function handleConnection(update, startBot) {
    const { connection, lastDisconnect, qr } = update;

    // QR Code management
    if (qr) {
        console.log('\n🔗 QR Code generated - Scan with WhatsApp:');
        qrcode.generate(qr, { small: true });

        // Save QR code to file
        const qrFilePath = path.join(process.cwd(), 'qr.png');
        QRCode.toFile(qrFilePath, qr, {
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            }
        }, (err) => {
            if (err) console.error('❌ Error saving QR code to file:', err);
            else console.log(`💾 QR code saved to: ${qrFilePath}`);
        });

        console.log('\n📱 Open WhatsApp > Settings > Linked devices > Link a device');
    }

    if (connection === 'close') {
        const statusCode = (lastDisconnect?.error)?.output?.statusCode;
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
        console.log(`❌ Connection closed (Status: ${statusCode})`);
        console.log('Reconnecting:', shouldReconnect);

        if (shouldReconnect) {
            startBot();
        }
    } else if (connection === 'open') {
        console.log('✅ WhatsApp bot connected successfully!');
    } else if (connection === 'connecting') {
        console.log('🔄 Connecting...');
    }
}

module.exports = {
    handleConnection
};
