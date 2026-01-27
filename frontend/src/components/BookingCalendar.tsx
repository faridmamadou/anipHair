import { useState } from 'react';
import { motion } from 'framer-motion';
import { format, addDays, startOfToday, isSameDay } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Calendar as CalendarIcon, Clock, CheckCircle2 } from 'lucide-react';

const TIME_SLOTS = [
    "09:00", "10:30", "13:00", "14:30", "16:00", "17:30"
];

export function BookingCalendar() {
    const [selectedDate, setSelectedDate] = useState(startOfToday());
    const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
    const [isBooked, setIsBooked] = useState(false);

    const next7Days = Array.from({ length: 7 }, (_, i) => addDays(startOfToday(), i));

    const handleBooking = () => {
        if (selectedSlot) {
            setIsBooked(true);
            setTimeout(() => setIsBooked(false), 5000);
        }
    };

    return (
        <section id="booking" className="py-24 bg-brand-linen relative">
            <div className="container mx-auto px-6 max-w-4xl">
                <div className="text-center mb-16">
                    <h2 className="text-brand-gold font-serif text-xl font-bold mb-4 uppercase tracking-widest">Prenez votre temps</h2>
                    <h3 className="text-4xl md:text-5xl font-serif font-black text-brand-charcoal mb-6">Réserver votre séance</h3>
                    <p className="text-brand-charcoal/60 max-w-lg mx-auto">
                        Sélectionnez une date et un créneau horaire pour votre transformation. Nous vous confirmerons le rendez-vous par SMS.
                    </p>
                </div>

                <div className="bg-white rounded-[3rem] shadow-2xl overflow-hidden border border-brand-gold/10 p-8 md:p-12">
                    {!isBooked ? (
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

                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    disabled={!selectedSlot}
                                    onClick={handleBooking}
                                    className={`w-full py-5 rounded-2xl font-black text-lg transition-all ${selectedSlot
                                        ? 'bg-brand-charcoal text-brand-linen shadow-xl hover:shadow-2xl'
                                        : 'bg-brand-linen text-brand-charcoal/30 cursor-not-allowed'
                                        }`}
                                >
                                    Confirmer le rendez-vous
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
                                Merci pour votre confiance. Vous recevrez un SMS de confirmation pour le <strong>{format(selectedDate, 'd MMMM', { locale: fr })}</strong> à <strong>{selectedSlot}</strong>.
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
