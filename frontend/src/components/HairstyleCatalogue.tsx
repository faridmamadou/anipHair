import { motion } from 'framer-motion';
import { Clock, Tag, ChevronRight } from 'lucide-react';

const HAIRSTYLES = [
    {
        id: 1,
        name: "Coiffe Afro",
        price: "85€",
        duration: "4h",
        image: "/images/afro.jpg",
        category: "Protection"
    },
    {
        id: 2,
        name: "Nattes Collées",
        price: "50€",
        duration: "2h",
        image: "/images/tresses-collees.jpg",
        category: "Classique"
    },
    {
        id: 3,
        name: "Coupe Courte",
        price: "120€",
        duration: "6h",
        image: "/images/courte.jpg",
        category: "Longue tenue"
    },
    {
        id: 4,
        name: "Twists Passion",
        price: "95€",
        duration: "3h30",
        image: "/images/large-twists.jpg",
        category: "Moderne"
    },
    {
        id: 5,
        name: "Chignon Haut",
        price: "45€",
        duration: "1h",
        image: "/images/chignon.jpg",
        category: "Événement"
    },
    {
        id: 6,
        name: "Cheveux Bouclés",
        price: "65€",
        duration: "2h30",
        image: "/images/curly.jpg",
        category: "Artistique"
    }
];

export function HairstyleCatalogue({ onSelectStyle }: { onSelectStyle: (id: number) => void }) {
    const handleSelect = (id: number) => {
        onSelectStyle(id);
        const bookingSection = document.getElementById('booking');
        if (bookingSection) {
            bookingSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <section id="catalogue" className="py-24 bg-white relative">
            <div className="container mx-auto px-6">
                <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
                    <div className="max-w-xl">
                        <h2 className="text-brand-gold font-serif text-xl font-bold mb-4 uppercase tracking-widest">Le Catalogue</h2>
                        <h3 className="text-4xl md:text-5xl font-serif font-black text-brand-charcoal leading-tight">
                            Choisissez votre prochain style signature
                        </h3>
                    </div>
                    <p className="text-brand-charcoal/50 font-medium max-w-xs">
                        Chaque réalisation est unique et adaptée à la texture de vos cheveux.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                    {HAIRSTYLES.map((style, index) => (
                        <motion.div
                            key={style.id}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="group"
                        >
                            <div className="relative aspect-square rounded-3xl overflow-hidden mb-6 shadow-xl group-hover:shadow-2xl transition-all h-[400px]">
                                <img
                                    src={style.image}
                                    alt={style.name}
                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-brand-charcoal/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-8">
                                    <button
                                        onClick={() => handleSelect(style.id)}
                                        className="w-full bg-brand-gold text-brand-charcoal font-bold py-3 rounded-xl flex items-center justify-center gap-2 transform translate-y-4 group-hover:translate-y-0 transition-transform"
                                    >
                                        Réserver ce style <ChevronRight className="w-5 h-5" />
                                    </button>
                                </div>
                                <div className="absolute top-4 left-4 bg-brand-linen/90 backdrop-blur-sm px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider text-brand-gold-dark border border-brand-gold/20">
                                    {style.category}
                                </div>
                            </div>

                            <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="text-2xl font-serif font-bold text-brand-charcoal mb-2">{style.name}</h4>
                                    <div className="flex gap-4">
                                        <span className="flex items-center gap-1.5 text-brand-charcoal/60 text-sm font-medium">
                                            <Clock className="w-4 h-4 text-brand-gold" />
                                            {style.duration}
                                        </span>
                                        <span className="flex items-center gap-1.5 text-brand-charcoal/60 text-sm font-medium">
                                            <Tag className="w-4 h-4 text-brand-gold" />
                                            {style.price}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
