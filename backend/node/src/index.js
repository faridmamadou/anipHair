require('dotenv').config();
const WhatsAppBot = require('./WhatsAppBot');

// Bot startup
const bot = new WhatsAppBot();
bot.startBot().catch(console.error);

// Graceful shutdown handling
process.on('SIGINT', () => {
    console.log('\n🛑 Stopping bot...');
    bot.listAudioFiles();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Stopping bot (SIGTERM)...');
    process.exit(0);
});
