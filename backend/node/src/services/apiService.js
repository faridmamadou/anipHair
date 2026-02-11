// backend/node/src/services/apiService.js
const axios = require('axios');
const FormData = require('form-data');

/**
 * Service pour envoyer des messages (texte ou audio) à FastAPI
 */
class APIService {
    constructor() {
        this.baseURL = process.env.API_BASE_URL || 'http://localhost:8000';
        this.timeout = 30000; // 30 secondes
    }

    /**
     * Envoie un message texte à FastAPI
     * @param {string} message - Le contenu du message
     * @param {string} senderId - L'ID de l'expéditeur (numéro WhatsApp)
     * @returns {Promise<Object>} - Réponse de l'API
     */
    async sendTextMessage(message, senderId) {
        try {
            console.log(`📤 Envoi message texte de ${senderId}`);

            const response = await axios.post(
                `${this.baseURL}/messages/receive`,
                {
                    type: 'text',
                    message: message,
                    sender_id: senderId
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: this.timeout
                }
            );

            console.log('✅ Message texte envoyé avec succès');
            return response.data;

        } catch (error) {
            console.error('❌ Erreur envoi texte:', error.message);
            if (error.response) {
                console.error('Détails:', error.response.data);
            }
            throw error;
        }
    }

    /**
     * Envoie un fichier audio à FastAPI
     * @param {Buffer} audioBuffer - Le buffer contenant l'audio
     * @param {string} senderId - L'ID de l'expéditeur
     * @param {string} mimetype - Type MIME de l'audio (ex: 'audio/ogg')
     * @returns {Promise<Object>} - Réponse de l'API
     */
    async sendAudioMessage(audioInfo, senderId, mimetype = 'audio/ogg') {
        try {
            console.log(`📤 Envoi audio de ${senderId} (${audioInfo.buffer.length} bytes)`);

            const form = new FormData();

            // Ajouter les champs du formulaire
            form.append('type', 'audio');
            form.append('sender_id', senderId);

            // Ajouter le fichier audio (Buffer en mémoire)
            form.append('file', audioInfo.buffer, {
                filename: `audio_${Date.now()}.ogg`,
                contentType: mimetype
            });

            const response = await axios.post(
                `${this.baseURL}/messages/receive`,
                form,
                {
                    headers: {
                        ...form.getHeaders()
                    },
                    timeout: this.timeout,
                    maxContentLength: Infinity,
                    maxBodyLength: Infinity
                }
            );

            console.log('✅ Audio envoyé avec succès');
            return response.data;

        } catch (error) {
            console.error('❌ Erreur envoi audio:', error.message);
            if (error.response) {
                console.error('Détails:', error.response.data);
            }
            throw error;
        }
    }

    /**
     * Méthode générique pour envoyer n'importe quel type de message
     * @param {Object} params - Paramètres du message
     * @returns {Promise<Object>}
     */
    async sendMessage(params) {
        const { type, content, senderId, mimetype } = params;

        if (type === 'text') {
            return await this.sendTextMessage(content, senderId);
        } else if (type === 'audio') {
            return await this.sendAudioMessage(content, senderId, mimetype);
        } else {
            throw new Error(`Type de message non supporté: ${type}`);
        }
    }
}

// Export singleton
module.exports = new APIService();