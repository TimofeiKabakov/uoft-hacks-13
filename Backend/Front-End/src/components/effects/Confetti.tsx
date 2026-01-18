/**
 * Confetti Celebration Effect
 * 
 * Animated confetti burst for celebration moments.
 */

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

interface ConfettiProps {
  trigger: boolean;
  duration?: number;
  pieces?: number;
}

const COLORS = [
  'hsl(184, 55%, 52%)', // Primary teal
  'hsl(312, 42%, 26%)', // Accent plum
  'hsl(142, 71%, 45%)', // Success green
  'hsl(38, 92%, 50%)',  // Warning amber
  'hsl(40, 33%, 94%)',  // Beige
];

interface ConfettiPiece {
  id: number;
  x: number;
  color: string;
  rotation: number;
  scale: number;
  shape: 'square' | 'circle' | 'triangle';
}

export function Confetti({ trigger, duration = 3000, pieces = 50 }: ConfettiProps) {
  const [confettiPieces, setConfettiPieces] = useState<ConfettiPiece[]>([]);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (trigger && !isActive) {
      setIsActive(true);
      
      const newPieces: ConfettiPiece[] = Array.from({ length: pieces }).map((_, i) => ({
        id: i,
        x: Math.random() * 100,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        rotation: Math.random() * 360,
        scale: 0.5 + Math.random() * 0.5,
        shape: ['square', 'circle', 'triangle'][Math.floor(Math.random() * 3)] as ConfettiPiece['shape'],
      }));
      
      setConfettiPieces(newPieces);
      
      setTimeout(() => {
        setIsActive(false);
        setConfettiPieces([]);
      }, duration);
    }
  }, [trigger, duration, pieces, isActive]);

  return (
    <AnimatePresence>
      {isActive && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {confettiPieces.map((piece) => (
            <motion.div
              key={piece.id}
              initial={{
                x: `${piece.x}vw`,
                y: '-10%',
                rotate: 0,
                scale: piece.scale,
                opacity: 1,
              }}
              animate={{
                y: '110vh',
                rotate: piece.rotation + 720,
                opacity: [1, 1, 0],
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: 2 + Math.random() * 2,
                ease: 'linear',
                delay: Math.random() * 0.5,
              }}
              style={{
                position: 'absolute',
                backgroundColor: piece.color,
                width: piece.shape === 'circle' ? 12 : 10,
                height: piece.shape === 'circle' ? 12 : 10,
                borderRadius: piece.shape === 'circle' ? '50%' : piece.shape === 'triangle' ? '0' : '2px',
                clipPath: piece.shape === 'triangle' ? 'polygon(50% 0%, 0% 100%, 100% 100%)' : undefined,
              }}
            />
          ))}
        </div>
      )}
    </AnimatePresence>
  );
}
