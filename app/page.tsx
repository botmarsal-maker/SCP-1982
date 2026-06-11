import Image from "next/image";

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-black text-white selection:bg-indigo-500/30">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start max-w-2xl text-center sm:text-left z-10">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Project Telegram Bot Menfess Telah Siap! 🚀
        </h1>
        <p className="text-lg text-gray-300 leading-relaxed">
          Source code bot Anda telah dihasilkan secara كامل (lengkap) menggunakan Python dan <code className="bg-gray-800 px-2 py-0.5 rounded text-sm text-blue-300">aiogram 3.x.</code>
        </p>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl w-full">
          <h2 className="text-xl font-semibold mb-4 text-white">Langkah Selanjutnya:</h2>
          <ol className="list-decimal list-inside space-y-4 text-gray-400 marker:text-indigo-500">
            <li>
              <strong className="text-gray-200">Export Project:</strong> Klik ikon Vercel/Settings pada bagian kiri/kanan browser AI Studio lalu pilih "Export to ZIP" atau "Export to GitHub".
            </li>
            <li>
              <strong className="text-gray-200">Ekstrak File:</strong> Buka hasil export dan temukan folder <code>telegram_bot/</code> yang berisi seluruh source code.
            </li>
            <li>
              <strong className="text-gray-200">Deploy:</strong> Ikuti panduan lengkap deployment VPS menggunakan PM2 yang terlampir pada file <code className="text-indigo-400">DEPLOYMENT.md</code>.
            </li>
          </ol>
        </div>

        <div className="flex gap-4 items-center flex-col sm:flex-row w-full mt-4">
          <div className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-indigo-600 text-white gap-2 hover:bg-indigo-700 text-sm sm:text-base h-10 sm:h-12 px-5 sm:px-8 w-full sm:w-auto font-medium">
            Siap Untuk Di-Deploy
          </div>
        </div>
      </main>
      
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/10 blur-[120px] rounded-full" />
      </div>
    </div>
  );
}
