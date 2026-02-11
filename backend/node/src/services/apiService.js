const axios = require('axios');

const API_BASE_URL = process.env.API_BASE_URL;

async function sendToFastAPI(text, type, senderId) {
    try {
        const response = await axios.post(
            `${API_BASE_URL}/api/messages/receive`,
            {
                message: text,
                type: type,
                sender_id: senderId,
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error sending message to FastAPI:', error.message);
        return null;
    }
}

module.exports = {
    sendToFastAPI,
};