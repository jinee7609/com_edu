import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.SITE_URL ?? 'http://localhost:3000'),
  title: '2022 개정 정보과 인출 연습 100제',
  description: '정보·컴퓨터 중등교사 임용시험 대비: 문제를 풀고 정답과 해설을 확인하는 반응형 학습 사이트입니다.',
  openGraph: { title: '2022 개정 정보과 인출 연습 100제', description: '문제를 풀고, 답을 확인하고, 다시 인출하세요.', images: ['/og.png'] },
  twitter: { card: 'summary_large_image', title: '2022 개정 정보과 인출 연습 100제', description: '문제를 풀고, 답을 확인하고, 다시 인출하세요.', images: ['/og.png'] },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}
