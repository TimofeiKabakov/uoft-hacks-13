/**
 * Header Component
 * 
 * Main navigation header with logo, nav links, and theme toggle.
 */

import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import trajectoryLogo from '@/assets/trajectory-logo.png';
import { useTheme } from '@/hooks/useTheme';
import { Button } from '@/components/ui/button';
import { fadeInDown, buttonHover } from '@/lib/animations';

const navLinks = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/recommendations', label: 'Recommendations' },
  { path: '/about', label: 'About' },
];

export function Header() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <motion.header
      variants={fadeInDown}
      initial="hidden"
      animate="show"
      className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
    >
      <div className="max-w-7xl mx-auto">
        <div className="glass-card rounded-2xl px-6 py-3 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <motion.div
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <img 
                src={trajectoryLogo} 
                alt="Trajectory" 
                className="h-8 w-auto"
              />
            </motion.div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link key={link.path} to={link.path}>
                  <motion.div
                    variants={buttonHover}
                    initial="rest"
                    whileHover="hover"
                    whileTap="tap"
                    className={`
                      px-4 py-2 rounded-xl text-sm font-medium transition-colors relative
                      ${isActive 
                        ? 'text-primary' 
                        : 'text-muted-foreground hover:text-foreground'
                      }
                    `}
                  >
                    {link.label}
                    {isActive && (
                      <motion.div
                        layoutId="activeNav"
                        className="absolute inset-0 bg-primary/10 rounded-xl -z-10"
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <motion.button
              variants={buttonHover}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
              onClick={toggleTheme}
              className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center hover:bg-muted/80 transition-colors"
              aria-label="Toggle theme"
            >
              <motion.div
                initial={false}
                animate={{ rotate: theme === 'dark' ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                {theme === 'light' ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
              </motion.div>
            </motion.button>

            {/* CTA Button */}
            <Link to="/evaluate">
              <Button className="rounded-xl font-medium">
                Start Evaluation
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
