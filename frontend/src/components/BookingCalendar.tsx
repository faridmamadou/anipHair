import { useState } from 'react';
import { motion } from 'framer-motion';
import { format, addDays, startOfToday, isSameDay, setHours, setMinutes } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Calendar as CalendarIcon, Clock, CheckCircle2, User, Phone, Loader2 } from 'lucide-react';

const TIME_SLOTS = [
    "09:00", "10:30", "13:00", "14:30", "16:00", "17:30"
];

export function BookingCalendar({ styleId }: { styleId: number | null }) {
    const [selectedDate, setSelectedDate] = useState(startOfToday());
    const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
    const [customerName, setCustomerName] = useState("");
    const [telephone, setTelephone] = useState("");
    const [isBooked, setIsBooked] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const next7Days = Array.from({ length: 7 }, (_, i) => addDays(startOfToday(), i));

    const handleBooking = async () => {
        if (!selectedSlot || !customerName || !telephone) {
            setError("Veuillez remplir tous les champs.");
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const [hours, minutes] = selectedSlot.split(':').map(Number);
            const bookingDate = setMinutes(setHours(selectedDate, hours), minutes);

            const response = await fetch('http://localhost:8000/whatsapp/appointments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    style_id: styleId || 1, // Default to first if none selected
                    customer_name: customerName,
                    telephone: telephone,
                    date: bookingDate.toISOString(),
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Une erreur est survenue lors de la réservation.");
            }

            setIsBooked(true);
            // Reset form
            setCustomerName("");
            setTelephone("");
            setSelectedSlot(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="booking" className="py-24 bg-brand-linen relative">
            <div className="container mx-auto px-6 max-w-4xl">
                <div className="text-center mb-16">
                    <h2 className="text-brand-gold font-serif text-xl font-bold mb-4 uppercase tracking-widest">Prenez votre temps</h2>
                    <h3 className="text-4xl md:text-5xl font-serif font-black text-brand-charcoal mb-6">Réserver votre séance</h3>
                    <p className="text-brand-charcoal/60 max-w-lg mx-auto">
                        Sélectionnez une date et un créneau horaire. Nous vous confirmerons le rendez-vous par WhatsApp.
                    </p>
                </div>

                <div className="bg-white rounded-[3rem] shadow-2xl overflow-hidden border border-brand-gold/10 p-8 md:p-12">
                    {!isBooked ? (
                        <div className="space-y-12">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                {/* Date Selection */}
                                <div>
                                    <div className="flex items-center gap-3 mb-6">
                                        <CalendarIcon className="w-6 h-6 text-brand-gold" />
                                        <h4 className="text-xl font-serif font-bold">1. Choisir la date</h4>
                                    </div>
                                    <div className="space-y-3">
                                        {next7Days.map((date) => (
                                            <button
                                                key={date.toString()}
                                                onClick={() => { setSelectedDate(date); setSelectedSlot(null); }}
                                                className={`w-full flex justify-between items-center p-4 rounded-2xl border-2 transition-all ${isSameDay(date, selectedDate)
                                                    ? 'border-brand-gold bg-brand-gold/5 text-brand-charcoal'
                                                    : 'border-transparent bg-brand-linen/50 hover:border-brand-gold/30'
                                                    }`}
                                            >
                                                <span className="font-bold capitalize">{format(date, 'EEEE d MMMM', { locale: fr })}</span>
                                                {isSameDay(date, selectedDate) && <CheckCircle2 className="w-5 h-5 text-brand-gold" />}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Time Selection */}
                                <div>
                                    <div className="flex items-center gap-3 mb-6">
                                        <Clock className="w-6 h-6 text-brand-gold" />
                                        <h4 className="text-xl font-serif font-bold">2. Choisir l'heure</h4>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3 mb-10">
                                        {TIME_SLOTS.map((slot) => (
                                            <button
                                                key={slot}
                                                onClick={() => setSelectedSlot(slot)}
                                                className={`p-4 rounded-2xl border-2 font-bold transition-all ${selectedSlot === slot
                                                    ? 'border-brand-gold bg-brand-gold text-brand-charcoal shadow-lg shadow-brand-gold/20'
                                                    : 'border-transparent bg-brand-linen/50 hover:border-brand-gold/30 text-brand-charcoal/60'
                                                    }`}
                                            >
                                                {slot}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Customer Info */}
                            <div className="border-t border-brand-linen pt-12">
                                <div className="flex items-center gap-3 mb-8">
                                    <User className="w-6 h-6 text-brand-gold" />
                                    <h4 className="text-xl font-serif font-bold">3. Vos informations</h4>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                                    <div className="space-y-2">
                                        <label className="text-sm font-bold text-brand-charcoal/60 ml-2">Nom complet</label>
                                        <div className="relative">
                                            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-gold/50" />
                                            <input
                                                type="text"
                                                value={customerName}
                                                onChange={(e) => setCustomerName(e.target.value)}
                                                placeholder="Jean Dupont"
                                                className="w-full pl-12 pr-4 py-4 rounded-2xl bg-brand-linen/30 border-2 border-transparent focus:border-brand-gold outline-none transition-all font-medium"
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-bold text-brand-charcoal/60 ml-2">Téléphone (WhatsApp)</label>
                                        <div className="relative">
                                            <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-gold/50" />
                                            <input
                                                type="tel"
                                                value={telephone}
                                                onChange={(e) => setTelephone(e.target.value)}
                                                placeholder="06 12 34 56 78"
                                                className="w-full pl-12 pr-4 py-4 rounded-2xl bg-brand-linen/30 border-2 border-transparent focus:border-brand-gold outline-none transition-all font-medium"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {error && (
                                    <motion.p
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="text-red-500 font-bold text-center mb-6"
                                    >
                                        {error}
                                    </motion.p>
                                )}

                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    disabled={!selectedSlot || !customerName || !telephone || isLoading}
                                    onClick={handleBooking}
                                    className={`w-full py-5 rounded-2xl font-black text-lg transition-all flex items-center justify-center gap-2 ${selectedSlot && customerName && telephone && !isLoading
                                        ? 'bg-brand-charcoal text-brand-linen shadow-xl hover:shadow-2xl'
                                        : 'bg-brand-linen text-brand-charcoal/30 cursor-not-allowed'
                                        }`}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="w-6 h-6 animate-spin" />
                                            Réservation en cours...
                                        </>
                                    ) : (
                                        'Confirmer le rendez-vous'
                                    )}
                                </motion.button>
                            </div>
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-center py-12"
                        >
                            <div className="w-24 h-24 bg-brand-gold/20 text-brand-gold rounded-full flex items-center justify-center mx-auto mb-8">
                                <CheckCircle2 className="w-12 h-12" />
                            </div>
                            <h4 className="text-3xl font-serif font-bold mb-4">Rendez-vous réservé !</h4>
                            <p className="text-brand-charcoal/60 max-w-sm mx-auto mb-8">
                                Merci pour votre confiance. Vous recevrez un message de confirmation sur WhatsApp pour le <strong>{format(selectedDate, 'd MMMM', { locale: fr })}</strong> à <strong>{selectedSlot}</strong>.
                            </p>
                            <button
                                onClick={() => setIsBooked(false)}
                                className="text-brand-gold font-bold hover:underline"
                            >
                                Prendre un autre rendez-vous
                            </button>
                        </motion.div>
                    )}
                </div>
            </div>
        </section>
    );
}
