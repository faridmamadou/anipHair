import { Scissors, Instagram, Facebook, Phone, Mail } from 'lucide-react';

export function Footer() {
    return (
        <footer id="about" className="bg-brand-charcoal text-brand-linen pt-20 pb-10">
            <div className="container mx-auto px-6">
                <div className="grid md:grid-cols-4 gap-12 mb-16">
                    <div className="col-span-2">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="p-1 bg-brand-gold rounded">
                                <Scissors className="w-5 h-5 text-brand-charcoal" />
                            </div>
                            <span className="text-2xl font-serif font-bold tracking-tight">AnipHair</span>
                        </div>
                        <p className="text-brand-linen/60 max-w-sm mb-8">
                            Expertise et passion au service de votre chevelure. Nous créons des styles qui racontent votre histoire avec précision et élégance.
                        </p>
                        <div className="flex gap-4">
                            <a href="#" className="p-3 border border-brand-linen/10 rounded-full hover:bg-brand-gold hover:text-brand-charcoal transition-all">
                                <Instagram className="w-5 h-5" />
                            </a>
                            <a href="#" className="p-3 border border-brand-linen/10 rounded-full hover:bg-brand-gold hover:text-brand-charcoal transition-all">
                                <Facebook className="w-5 h-5" />
                            </a>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-brand-gold font-serif text-xl mb-6">Navigation</h4>
                        <ul className="space-y-4 text-brand-linen/60">
                            <li><a href="#" className="hover:text-brand-gold transition-colors">Accueil</a></li>
                            <li><a href="#catalogue" className="hover:text-brand-gold transition-colors">Catalogue</a></li>
                            <li><a href="#booking" className="hover:text-brand-gold transition-colors">Prendre RDV</a></li>
                            <li><a href="#" className="hover:text-brand-gold transition-colors">Mentions Légales</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-brand-gold font-serif text-xl mb-6">Contact</h4>
                        <ul className="space-y-4 text-brand-linen/60">
                            <li className="flex items-center gap-3">
                                <Phone className="w-4 h-4 text-brand-gold" />
                                +33 7 00 00 00 00
                            </li>
                            <li className="flex items-center gap-3">
                                <Mail className="w-4 h-4 text-brand-gold" />
                                contact@aniphair.com
                            </li>
                            <li className="mt-4">
                                123 Boulevard de la Coiffure<br />
                                75000 Paris, France
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-brand-linen/10 pt-10 text-center text-brand-linen/40 text-sm">
                    <p>© {new Date().getFullYear()} AnipHair. Tous droits réservés.</p>
                </div>
            </div>
        </footer>
    );
}
