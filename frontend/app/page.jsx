import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center bg-gradient-to-b from-antares-black via-antares-dark to-antares-black overflow-hidden">
        {/* Fondo decorativo */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-10 w-64 h-64 bg-antares-gold rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-antares-amber rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
          <h1 className="font-display text-6xl md:text-8xl text-antares-gold mb-6 tracking-wider">
            LOS FLACHEROS
          </h1>
          <p className="text-xl md:text-2xl text-antares-cream mb-4 font-light italic">
            "Arte en cada trago, tradición en cada lote"
          </p>
          <p className="text-antares-text-muted text-lg mb-12 max-w-2xl mx-auto">
            Cervecería artesanal uruguaya elaborada con pasión, ingredientes premium y recetas tradicionales que honran el oficio cervecero.
          </p>
          
          <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
            <Link href="/login" className="btn-primary text-lg">
              Ingresar al Catálogo
            </Link>
            <Link href="#nosotros" className="btn-secondary text-lg">
              Conocé Nuestra Historia
            </Link>
          </div>
        </div>
      </section>

      {/* Quiénes Somos */}
      <section id="nosotros" className="py-20 bg-antares-dark">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="font-display text-5xl text-antares-gold mb-4">Nuestra Historia</h2>
            <div className="gold-divider max-w-xs mx-auto"></div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-lg text-antares-text leading-relaxed mb-6">
                <span className="text-antares-gold font-bold text-2xl">Cervecería Los Flacheros</span> nació de la pasión por la cerveza artesanal y el deseo de crear algo único. Cada lote es elaborado con dedicación, utilizando ingredientes seleccionados y técnicas tradicionales.
              </p>
              <p className="text-lg text-antares-text leading-relaxed mb-6">
                Nuestra misión es ofrecer cervezas de calidad premium que capturen la esencia del auténtico sabor artesanal, desde nuestras IPA lupuladas hasta nuestras Stout robustas.
              </p>
              <p className="text-lg text-antares-text leading-relaxed">
                Cada botella cuenta una historia de dedicación, tradición y el amor por el buen hacer cervecero.
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-antares-black/50 p-6 rounded-lg border border-antares-gold/20">
                <div className="text-4xl font-bold text-antares-gold mb-2">8</div>
                <div className="text-antares-text-muted uppercase tracking-wider text-sm">Variedades</div>
              </div>
              <div className="bg-antares-black/50 p-6 rounded-lg border border-antares-gold/20">
                <div className="text-4xl font-bold text-antares-gold mb-2">100%</div>
                <div className="text-antares-text-muted uppercase tracking-wider text-sm">Artesanal</div>
              </div>
              <div className="bg-antares-black/50 p-6 rounded-lg border border-antares-gold/20">
                <div className="text-4xl font-bold text-antares-gold mb-2">4.8</div>
                <div className="text-antares-text-muted uppercase tracking-wider text-sm">Valoración</div>
              </div>
              <div className="bg-antares-black/50 p-6 rounded-lg border border-antares-gold/20">
                <div className="text-4xl font-bold text-antares-gold mb-2">2020</div>
                <div className="text-antares-text-muted uppercase tracking-wider text-sm">Fundada</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cervezas Destacadas Preview */}
      <section className="py-20 bg-antares-black">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="font-display text-5xl text-antares-gold mb-4">Nuestras Cervezas</h2>
            <p className="text-antares-text-muted text-lg">Descubrí nuestra selección artesanal</p>
            <div className="gold-divider max-w-xs mx-auto mt-6"></div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-antares-surface p-8 rounded-lg border border-antares-gold/20 text-center hover:border-antares-gold transition-colors">
              <div className="text-5xl mb-4">🍺</div>
              <h3 className="font-display text-2xl text-antares-gold mb-3">IPA del Flachero</h3>
              <p className="text-antares-text-muted">India Pale Ale con intenso perfil lupulado, notas cítricas y amargor equilibrado</p>
            </div>
            
            <div className="bg-antares-surface p-8 rounded-lg border border-antares-gold/20 text-center hover:border-antares-gold transition-colors">
              <div className="text-5xl mb-4">🍻</div>
              <h3 className="font-display text-2xl text-antares-gold mb-3">Stout de la Casa</h3>
              <p className="text-antares-text-muted">Cerveza oscura robusta con notas a café, chocolate y maltas tostadas</p>
            </div>
            
            <div className="bg-antares-surface p-8 rounded-lg border border-antares-gold/20 text-center hover:border-antares-gold transition-colors">
              <div className="text-5xl mb-4">🥂</div>
              <h3 className="font-display text-2xl text-antares-gold mb-3">Pilsener del Flachero</h3>
              <p className="text-antares-text-muted">Lager clásica, fresca y equilibrada, perfecta para cualquier ocasión</p>
            </div>
          </div>
          
          <div className="text-center">
            <Link href="/login" className="btn-primary text-lg inline-block">
              Ver Catálogo Completo
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-gradient-to-r from-antares-dark via-antares-gray to-antares-dark">
        <div className="container mx-auto px-6 text-center max-w-4xl">
          <h2 className="font-display text-5xl text-antares-gold mb-6">¿Listo para descubrir el sabor auténtico?</h2>
          <p className="text-xl text-antares-text mb-8">Ingresá al catálogo y explorá todas nuestras variedades artesanales</p>
          <Link href="/login" className="btn-primary text-lg">
            Acceder al Catálogo
          </Link>
        </div>
      </section>
    </div>
  );
}
