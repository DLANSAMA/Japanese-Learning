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
    // p-2 padding matches the top-2 left-2 offset of the SVG for alignment
    // bg-paper/50 provides subtle background contrast
    <div className="relative inline-flex flex-col items-center select-none p-2 rounded-lg bg-paper/50 backdrop-blur-sm border border-tatami">
      {/*
        SVG positioning:
        - absolute top-2 left-2: offsets the SVG by the parent's padding (p-2 = 0.5rem = 8px)
        - This ensures the SVG coordinates (based on padding logic) align with the text content
      */}
      <svg width={totalWidth} height={height} className="absolute top-2 left-2 pointer-events-none">
        {/* Pitch contour line: stroke-crimson for visibility */}
        <path d={pathD} className="stroke-crimson" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((pt, i) => (
            <circle
                key={i}
                cx={pt.x}
                cy={pt.y}
                r="5"
                // High pitch = Crimson, Low pitch = Charcoal (theme-aware)
                className={pt.p === 'H' ? "fill-crimson stroke-paper" : "fill-charcoal stroke-paper"}
                strokeWidth="2"
            />
        ))}
        {/* Draw drop indicator */}
        {points.map((pt, i) => {
            if (pt.p === 'H' && points[i+1] && points[i+1].p === 'L') {
                 // Drop happens after this character
                 const dropX = pt.x + charWidth / 2;
                 return (
                    <g key={`drop-${i}`}>
                        <line x1={dropX} y1={10} x2={dropX} y2={35} className="stroke-crimson" strokeWidth="2" strokeDasharray="4 2" />
                        <text x={dropX} y={45} fontSize="10" textAnchor="middle" className="fill-crimson">↘</text>
                    </g>
                 );
            }
            return null;
        })}
      </svg>
      {/*
        Text container:
        - pt-10 pushes the text below the pitch diagram
        - width matches SVG calculation
        - font-bold + text-charcoal ensures high contrast
      */}
      <div className="flex pt-10" style={{ width: totalWidth, paddingLeft: padding, paddingRight: padding }}>
        {kana.split('').map((char, i) => (
             <span key={i} className="text-2xl font-bold w-[40px] text-center inline-block text-charcoal">{char}</span>
        ))}
      </div>
    </div>
  );
};
