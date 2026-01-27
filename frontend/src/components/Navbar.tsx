import { Scissors } from 'lucide-react';

export function Navbar() {
    return (
        <nav className="fixed top-0 w-full z-50 bg-brand-charcoal/90 backdrop-blur-md border-b border-brand-gold/20 px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2 group cursor-pointer">
                <div className="p-1.5 bg-brand-gold rounded-lg transition-transform group-hover:rotate-12">
                    <Scissors className="w-5 h-5 text-brand-charcoal" />
                </div>
                <span className="text-2xl font-serif font-bold tracking-tight text-brand-linen">
                    Anip<span className="text-brand-gold underline decoration-brand-gold/30">Hair</span>
                </span>
            </div>

            <div className="hidden md:flex gap-8 text-brand-linen/80 font-medium">
                <a href="#catalogue" className="hover:text-brand-gold transition-colors">Catalogue</a>
                <a href="#booking" className="hover:text-brand-gold transition-colors">Rendez-vous</a>
                <a href="#about" className="hover:text-brand-gold transition-colors">À Propos</a>
            </div>

            <button className="bg-brand-gold text-brand-charcoal px-6 py-2 rounded-full font-bold hover:bg-brand-gold-light transition-all shadow-lg hover:shadow-brand-gold/20 transform hover:-translate-y-0.5">
                Réserver
            </button>
        </nav>
    );
}
