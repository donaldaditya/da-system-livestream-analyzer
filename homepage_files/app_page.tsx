export default function Home() {
  return (
    <main className="min-h-screen bg-white text-gray-900">

      {/* Nav */}
      <nav className="border-b border-gray-100 px-6 py-4 flex items-center justify-between max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-900 rounded-md flex items-center justify-center">
            <span className="text-white text-xs font-medium">DA</span>
          </div>
          <span className="text-sm font-medium">DA System</span>
        </div>
        <a
          href="https://www.linkedin.com/in/donaldaditya/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-gray-400 hover:text-gray-700 transition-colors"
        >
          Donald Aditya ↗
        </a>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-16">
        <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Decision Architecture</p>
        <h1 className="text-4xl font-medium tracking-tight leading-tight mb-6">
          AI tools built to<br />
          <span className="text-gray-400">extend human judgement</span>
        </h1>
        <p className="text-sm text-gray-500 max-w-lg leading-relaxed">
          DA System is a set of applied AI tools designed to make complex commercial decisions
          faster, safer, and more transparent — not to replace the people making them.
          Built for commerce teams operating in Southeast Asia.
        </p>
      </section>

      {/* Tools */}
      <section className="max-w-4xl mx-auto px-6 pb-20">
        <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Tools</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

          <a
            href="/creator-score"
            className="group block bg-white border border-gray-100 rounded-xl p-6 hover:border-gray-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs text-gray-400 uppercase tracking-wider">Tool 01</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">Live</span>
            </div>
            <div className="text-sm font-medium mb-2 group-hover:text-gray-600 transition-colors">
              Creator Score
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              Score and rank creators by ROI across TikTok Shop, Instagram, and Shopee.
              Upload exports or auto-fetch by handle.
            </p>
            <div className="mt-4 text-xs text-gray-300 group-hover:text-gray-500 transition-colors">
              Open tool →
            </div>
          </a>

          <a
            href="/livestream-analyzer/"
            className="group block bg-white border border-gray-100 rounded-xl p-6 hover:border-gray-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs text-gray-400 uppercase tracking-wider">Tool 02</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">New</span>
            </div>
            <div className="text-sm font-medium mb-2 group-hover:text-gray-600 transition-colors">
              Livestream Analyzer
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              Post-stream AI diagnosis for TikTok Shop and Shopee. Score, benchmark,
              coaching brief, and WhatsApp export.
            </p>
            <div className="mt-4 text-xs text-gray-300 group-hover:text-gray-500 transition-colors">
              Open tool →
            </div>
          </a>

        </div>
      </section>

      {/* About */}
      <section className="border-t border-gray-50 max-w-4xl mx-auto px-6 py-16">
        <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">About</p>
        <div className="max-w-xl">
          <p className="text-sm text-gray-600 leading-relaxed mb-3">
            Built by{" "}
            <a
              href="https://www.linkedin.com/in/donaldaditya/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-2 hover:text-gray-900 transition-colors"
            >
              Donald Aditya
            </a>
            . The goal is simple: make AI genuinely useful for the people doing
            the work — analysts, operators, managers — without adding complexity or
            obscuring the decision behind the output.
          </p>
          <p className="text-sm text-gray-400 leading-relaxed">
            Every tool here is designed around one principle: AI should clarify,
            not replace. The human stays in the loop. The model does the heavy lifting.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-50 max-w-4xl mx-auto px-6 py-6 flex items-center justify-between">
        <span className="text-xs text-gray-300">DA System</span>
        <a
          href="https://www.linkedin.com/in/donaldaditya/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-gray-300 hover:text-gray-500 transition-colors"
        >
          linkedin.com/in/donaldaditya
        </a>
      </footer>

    </main>
  );
}
