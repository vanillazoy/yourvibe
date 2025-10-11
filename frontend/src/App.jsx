// src/App.jsx
import React, { useState } from "react";

export default function App() {
  const [playlists] = useState([
    {
      id: 1,
      title: "🌙 Night Vibe",
      tag: "차분한 밤, 감성적인 노래들",
      cover:
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
    },
    {
      id: 2,
      title: "☀️ Morning Chill",
      tag: "햇살 아래 듣기 좋은 잔잔한 음악",
      cover:
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
    },
    {
      id: 3,
      title: "🔥 Energetic Beats",
      tag: "운동할 때 듣기 좋은 에너지 충전 트랙",
      cover:
        "https://images.unsplash.com/photo-1485579149621-3123dd979885?auto=format&fit=crop&w=800&q=80",
    },
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-vibe-bg to-black text-white flex flex-col items-center py-10 px-4">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold mb-3 text-vibe-accent drop-shadow-md">
          🎧 YourVibe
        </h1>
        <p className="text-gray-400 text-sm">나만의 감성 플레이리스트 공간</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-6xl">
        {playlists.map((room) => (
          <div
            key={room.id}
            className="group relative bg-vibe-card rounded-2xl overflow-hidden shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer"
          >
            <img
              src={room.cover}
              alt={room.title}
              className="w-full h-56 object-cover opacity-90 group-hover:opacity-100 transition"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent group-hover:from-black/40 transition"></div>
            <div className="absolute bottom-0 left-0 p-4">
              <h2 className="text-lg font-semibold mb-1">{room.title}</h2>
              <p className="text-sm text-gray-300">{room.tag}</p>
            </div>
          </div>
        ))}
      </section>

      <footer className="mt-16 text-gray-500 text-xs">
        © 2025 YourVibe. Feel your mood. 💫
      </footer>
    </div>
  );
}
