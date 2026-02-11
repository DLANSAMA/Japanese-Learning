import React from 'react';

export const PitchAccent = ({ kana, pattern }) => {
  if (!pattern || pattern.length !== kana.length) {
    return <span className="text-xl font-medium">{kana}</span>;
  }

  const charWidth = 40;
  const height = 50;
  const padding = 20;
  const totalWidth = kana.length * charWidth + padding * 2;

  const points = pattern.split('').map((p, i) => {
    const x = padding + i * charWidth + charWidth / 2;
    const y = p === 'H' ? 10 : 35;
    return { x, y, char: kana[i], p };
  });

  // Create path data
  let pathD = `M ${points[0].x} ${points[0].y}`;
  points.slice(1).forEach(pt => {
      pathD += ` L ${pt.x} ${pt.y}`;
  });

  return (
    <div className="relative inline-flex flex-col items-center select-none p-2 rounded-lg bg-white/50 backdrop-blur-sm border border-tatami">
      <svg width={totalWidth} height={height} className="absolute top-0 left-0 pointer-events-none">
        <path d={pathD} stroke="#BC002D" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((pt, i) => (
            <circle key={i} cx={pt.x} cy={pt.y} r="5" fill={pt.p === 'H' ? "#BC002D" : "#2D2A26"} stroke="white" strokeWidth="2" />
        ))}
        {/* Draw drop indicator */}
        {points.map((pt, i) => {
            if (pt.p === 'H' && points[i+1] && points[i+1].p === 'L') {
                 // Drop happens after this character
                 const dropX = pt.x + charWidth / 2;
                 return (
                    <g key={`drop-${i}`}>
                        <line x1={dropX} y1={10} x2={dropX} y2={35} stroke="#BC002D" strokeWidth="2" strokeDasharray="4 2" />
                        <text x={dropX} y={45} fontSize="10" textAnchor="middle" fill="#BC002D">↘</text>
                    </g>
                 );
            }
            return null;
        })}
      </svg>
      <div className="flex pt-10" style={{ width: totalWidth, paddingLeft: padding, paddingRight: padding }}>
        {kana.split('').map((char, i) => (
             <span key={i} className="text-2xl font-bold w-[40px] text-center inline-block">{char}</span>
        ))}
      </div>
    </div>
  );
};
