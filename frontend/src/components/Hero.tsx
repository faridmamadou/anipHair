import { motion } from 'framer-motion';

export function Hero() {
    return (
        <section className="relative h-[90vh] flex items-center justify-center overflow-hidden pt-20">
            {/* Background Decor */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-1/4 -left-20 w-96 h-96 bg-brand-gold/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-brand-gold-light/5 rounded-full blur-3xl animate-pulse delay-1000" />
            </div>

            <div className="container mx-auto px-6 z-10 grid md:grid-cols-2 gap-12 items-center">
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-6xl md:text-8xl font-serif font-black leading-tight mb-6 text-brand-charcoal">
                        Exprimez votre <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-gold-dark via-brand-gold to-brand-gold-light">
                            Élégance.
                        </span>
                    </h1>
                    <p className="text-xl text-brand-charcoal/70 mb-8 max-w-lg leading-relaxed">
                        AnipHair transforme vos cheveux en une œuvre d'art unique. Découvrez notre catalogue de coiffures d'exception et réservez votre moment de beauté.
                    </p>
                    <div className="flex gap-4">
                        <a
                            href="#catalogue"
                            className="bg-brand-charcoal text-brand-linen px-8 py-4 rounded-xl font-bold hover:shadow-xl transition-all"
                        >
                            Voir le catalogue
                        </a>
                        <a
                            href="#booking"
                            className="border-2 border-brand-charcoal text-brand-charcoal px-8 py-4 rounded-xl font-bold hover:bg-brand-charcoal hover:text-brand-linen transition-all"
                        >
                            Réserver rdv
                        </a>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 1 }}
                    className="relative"
                >
                    <div className="aspect-[4/5] rounded-[3rem] overflow-hidden shadow-2xl border-4 border-brand-gold/30">
                        <img
                            src="https://images.unsplash.com/photo-1560869713-7d0a29430803?auto=format&fit=crop&q=80&w=1000"
                            alt="Hairstyle Model"
                            className="w-full h-full object-cover grayscale-[0.2] hover:grayscale-0 transition-all duration-700"
                        />
                    </div>
                    {/* Decorative frame overlay */}
                    <div className="absolute -inset-4 border border-brand-gold/20 rounded-[3.5rem] -z-10" />
                </motion.div>
            </div>
        </section>
    );
}
