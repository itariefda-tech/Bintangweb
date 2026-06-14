export const mockDashboardItems = [
  { index: "01", title: "Profile settings", description: "Lengkapi identitas dan konteks pekerjaan.", href: "/member/profile" },
  { index: "02", title: "Notification center", description: "Lihat update akun dan aktivitas penting.", href: "/member/notifications" },
  { index: "03", title: "Order history", description: "Pantau invoice dan perjalanan pesanan.", href: "/member/orders" },
  { index: "04", title: "IT consultation", description: "Kelola ticket dan diskusi teknis.", href: "/member/consultation" },
  { index: "05", title: "Curated marketplace", description: "Kembali mencari solusi yang relevan.", href: "/marketplace" },
];

export const mockConsultations = [
  {
    number: "FRA-MOCK-001",
    subject: "Audit kebutuhan jaringan kantor",
    summary: "Contoh ticket untuk memperlihatkan hierarchy informasi dan status.",
    status: "Waiting review",
    category: "Network",
    updatedAt: "Mock data",
  },
];

export const mockNews = [
  {
    category: "Infrastructure",
    title: "Menyusun jaringan kantor tanpa membeli perangkat secara acak.",
    excerpt: "Kerangka awal untuk menilai user, traffic, coverage, keamanan, dan kebutuhan ekspansi.",
    readingTime: "5 min read",
    image: "/assets/images/futuristic_netcloud.webp",
  },
  {
    category: "Business Tech",
    title: "Kapan bisnis perlu sistem custom, dan kapan belum?",
    excerpt: "Cara membedakan masalah proses, integrasi, dan kebutuhan aplikasi yang benar-benar spesifik.",
    readingTime: "4 min read",
    image: "/assets/images/service-application.webp",
  },
];
