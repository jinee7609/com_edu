'use client';

import { useEffect, useMemo, useState } from 'react';
import { questions } from '../data/questions';

const sections = [
  { key: '전체', label: '전체 100', short: '전체' },
  { key: '중학교 정보', label: '중학교 정보', short: '중학교' },
  { key: '고등학교 정보', label: '고등학교 정보', short: '고등학교' },
  { key: '인공지능 기초', label: '인공지능 기초', short: 'AI 기초' },
  { key: '데이터 과학', label: '데이터 과학', short: '데이터' },
  { key: '소프트웨어와 생활', label: '소프트웨어와 생활', short: 'SW 생활' },
];
type Status = 'again' | 'done';

export default function Home() {
  const [section, setSection] = useState('전체');
  const [currentId, setCurrentId] = useState(1);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  const [statuses, setStatuses] = useState<Record<number, Status>>({});
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => { try { setDrafts(JSON.parse(localStorage.getItem('info-quiz-drafts') || '{}')); setRevealed(JSON.parse(localStorage.getItem('info-quiz-revealed') || '{}')); setStatuses(JSON.parse(localStorage.getItem('info-quiz-statuses') || '{}')); } finally { setHydrated(true); } }, []);
  useEffect(() => { if (hydrated) localStorage.setItem('info-quiz-drafts', JSON.stringify(drafts)); }, [drafts, hydrated]);
  useEffect(() => { if (hydrated) localStorage.setItem('info-quiz-revealed', JSON.stringify(revealed)); }, [revealed, hydrated]);
  useEffect(() => { if (hydrated) localStorage.setItem('info-quiz-statuses', JSON.stringify(statuses)); }, [statuses, hydrated]);
  const filtered = useMemo(() => section === '전체' ? questions : questions.filter(q => q.section.includes(section)), [section]);
  const currentIndex = Math.max(0, filtered.findIndex(q => q.id === currentId));
  const current = filtered[currentIndex] || filtered[0];
  const doneCount = filtered.filter(q => statuses[q.id] === 'done').length;
  const progress = Math.round((doneCount / filtered.length) * 100);
  const changeSection = (key: string) => { const next = key === '전체' ? questions : questions.filter(q => q.section.includes(key)); setSection(key); setCurrentId(next[0].id); };
  const move = (step: number) => { const next = Math.min(filtered.length - 1, Math.max(0, currentIndex + step)); setCurrentId(filtered[next].id); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const randomQuestion = () => { const pool = filtered.filter(q => statuses[q.id] !== 'done'); const source = pool.length ? pool : filtered; setCurrentId(source[Math.floor(Math.random() * source.length)].id); };
  if (!current) return null;
  return <main>
    <header className="topbar"><div className="brand"><span className="brand-mark">I</span><div><b>정보과 인출 연습</b><small>2022 개정 교육과정 · 100제</small></div></div><button className="shuffle" onClick={randomQuestion}>무작위 문제</button></header>
    <section className="study-shell">
      <aside className="sidebar"><p className="side-label">학습 범위</p><nav>{sections.map(item => <button key={item.key} className={section === item.key ? 'active' : ''} onClick={() => changeSection(item.key)}><span>{item.short}</span><small>{item.label}</small></button>)}</nav><div className="progress-card"><div><span>완료</span><b>{doneCount}/{filtered.length}</b></div><div className="progress-track"><i style={{ width: `${progress}%` }} /></div><small>{progress}% 학습했어요</small></div></aside>
      <section className="workspace">
        <div className="mobile-tabs">{sections.map(item => <button key={item.key} className={section === item.key ? 'active' : ''} onClick={() => changeSection(item.key)}>{item.short}</button>)}</div>
        <div className="question-meta"><div><span className="section-pill">{current.section.replace(/\s*\(.*\)/, '')}</span><span className="type-pill">{current.prompt.match(/^\[([^\]]+)\]/)?.[1] || '문제'}</span></div><strong>{currentIndex + 1} <small>/ {filtered.length}</small></strong></div>
        <article className="question-card"><p className="question-number">QUESTION {String(current.id).padStart(3, '0')}</p><h1>{current.prompt.replace(/^\[[^\]]+\]\s*/, '')}</h1>
          <label className="answer-box"><span>나의 답안</span><textarea value={drafts[current.id] || ''} onChange={e => setDrafts({ ...drafts, [current.id]: e.target.value })} placeholder="기억나는 내용을 먼저 말하거나 적어 보세요." /></label>
          {!revealed[current.id] ? <button className="reveal-button" onClick={() => setRevealed({ ...revealed, [current.id]: true })}>정답·해설 확인</button> : <section className="answer-panel" aria-live="polite"><p className="answer-label">예시 답안</p><p className="model-answer">{current.answer}</p><div className="answer-notes"><p><span>관련 내용·성취기준</span>{current.standard}</p><p><span>채점 핵심어</span>{current.keywords}</p></div><div className="self-check"><span>내 답을 확인했다면</span><div><button className={statuses[current.id] === 'again' ? 'selected again' : 'again'} onClick={() => setStatuses({ ...statuses, [current.id]: 'again' })}>다시 볼래요</button><button className={statuses[current.id] === 'done' ? 'selected done' : 'done'} onClick={() => setStatuses({ ...statuses, [current.id]: 'done' })}>알고 있어요</button></div></div></section>}
        </article>
        <div className="navigation"><button onClick={() => move(-1)} disabled={currentIndex === 0}>← 이전</button><button onClick={() => move(1)} disabled={currentIndex === filtered.length - 1}>다음 →</button></div>
        <details className="question-map"><summary>문항 목록에서 바로 이동</summary><div>{filtered.map(q => <button key={q.id} onClick={() => setCurrentId(q.id)} className={`${q.id === current.id ? 'current' : ''} ${statuses[q.id] || ''}`}>{q.id}</button>)}</div></details>
      </section>
    </section>
    <footer><p>답안과 학습 기록은 현재 기기에만 저장됩니다.</p><button onClick={() => { if (confirm('작성한 답안과 학습 기록을 모두 지울까요?')) { setDrafts({}); setRevealed({}); setStatuses({}); } }}>학습 기록 초기화</button></footer>
  </main>;
}
