import { useState } from 'react';
import { HairstyleCatalogue } from './components/HairstyleCatalogue';
import { BookingCalendar } from './components/BookingCalendar';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { Footer } from './components/Footer';
import './App.css';

function App() {
  const [selectedStyleId, setSelectedStyleId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-brand-linen bg-[url('https://www.transparenttextures.com/patterns/linen.png')]">
      <Navbar />
      <main>
        <Hero />
        <HairstyleCatalogue onSelectStyle={setSelectedStyleId} />
        <BookingCalendar styleId={selectedStyleId} />
      </main>
      <Footer />
    </div>
  );
}

export default App;
