/**
 * Bank Data Step
 * 
 * Step 3: Plaid-style bank sign-in for connecting financial accounts.
 * Uses Plaid Sandbox API for demo banking data with various scenarios.
 */

import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  ArrowLeft,
  Building2,
  Lock,
  Eye,
  EyeOff,
  Search,
  Shield,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { usePlaidLink } from 'react-plaid-link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { GlassCard } from '@/components/ui/GlassCard';
import { staggerContainer, fadeInUp, scaleIn } from '@/lib/animations';
import { api } from '@/api/client';

// Mock bank institutions for Plaid Sandbox
const SANDBOX_INSTITUTIONS = [
  { id: 'plaid', name: 'Plaid Bank', logo: '🔗', color: '#00D084' },
  { id: 'chase', name: 'Chase', logo: '🏦', color: '#117ACA' },
  { id: 'bofa', name: 'Bank of America', logo: '🏛️', color: '#E31837' },
  { id: 'wells', name: 'Wells Fargo', logo: '🏧', color: '#D71E28' },
  { id: 'citi', name: 'Citibank', logo: '🏢', color: '#003B70' },
  { id: 'usbank', name: 'US Bank', logo: '🏦', color: '#0C2340' },
  { id: 'capital', name: 'Capital One', logo: '💳', color: '#004977' },
  { id: 'pnc', name: 'PNC Bank', logo: '🏛️', color: '#FF6200' },
  { id: 'td', name: 'TD Bank', logo: '🏧', color: '#34A853' },
];

interface BankDataStepProps {
  applicationId: string | null;
  onNext: () => void;
  onBack: () => void;
}

type SignInState = 'select-bank' | 'credentials' | 'connecting' | 'success';

interface SelectedBank {
  id: string;
  name: string;
  logo: string;
  color: string;
}

export function BankDataStep({ applicationId, onNext, onBack }: BankDataStepProps) {
  const [state, setState] = useState<SignInState>('select-bank');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBank, setSelectedBank] = useState<SelectedBank | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [linkToken, setLinkToken] = useState<string | null>(null);

  // Fetch link token when component mounts
  useEffect(() => {
    if (applicationId && !linkToken) {
      console.log('Fetching link token for application:', applicationId);
      fetch(`http://localhost:8000/api/v1/applications/${applicationId}/plaid-link-token`, {
        method: 'POST',
      })
        .then(res => {
          console.log('Link token response status:', res.status);
          return res.json();
        })
        .then(data => {
          console.log('Link token received:', data.link_token?.substring(0, 20) + '...');
          setLinkToken(data.link_token);
        })
        .catch(err => console.error('Failed to get link token:', err));
    }
  }, [applicationId, linkToken]);

  // Handle successful Plaid Link flow
  const onSuccess = useCallback(async (public_token: string) => {
    if (!applicationId) return;

    setIsConnecting(true);
    setState('connecting');

    try {
      const response = await api.connectPlaid(applicationId, public_token);

      if (response.success) {
        setState('success');
        setIsConnecting(false);
        setTimeout(() => onNext(), 1500);
      } else {
        throw new Error(response.error?.message || 'Failed to connect bank');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setState('credentials');
      setIsConnecting(false);
    }
  }, [applicationId, onNext]);

  // Initialize Plaid Link
  const config = {
    token: linkToken || '',
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  const filteredBanks = SANDBOX_INSTITUTIONS.filter(bank =>
    bank.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleBankSelect = (bank: SelectedBank) => {
    setSelectedBank(bank);
    setState('credentials');
    setError(null);
  };

  const handleSignIn = async () => {
    if (!username || !password) return;
    if (!applicationId) {
      setError('No application ID found. Please restart the evaluation.');
      return;
    }

    setIsConnecting(true);
    setState('connecting');
    setError(null);

    // For sandbox mode, we'll use Plaid's sandbox test credentials
    // In a real app, this would open Plaid Link modal
    // For sandbox: user_good/pass_good creates a successful connection

    try {
      // Simulate Plaid sandbox flow by calling a sandbox endpoint
      // that generates test data based on the username
      const response = await fetch(`http://localhost:8000/api/v1/applications/${applicationId}/plaid-sandbox`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          password,
          institution_id: selectedBank?.id || 'ins_109508'
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setState('success');
        setIsConnecting(false);
        setTimeout(() => onNext(), 1500);
      } else {
        throw new Error(data.error || 'Failed to connect bank');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setState('credentials');
      setIsConnecting(false);
    }
  };

  const handleBackToSearch = () => {
    setState('select-bank');
    setSelectedBank(null);
    setUsername('');
    setPassword('');
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="max-w-xl mx-auto"
    >
      <motion.div variants={fadeInUp} className="text-center mb-6">
        <h2 className="text-2xl font-bold mb-2">Connect Your Bank</h2>
        <p className="text-muted-foreground">
          Securely link your accounts using Plaid
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Bank Selection */}
        {state === 'select-bank' && (
          <motion.div
            key="select-bank"
            variants={scaleIn}
            initial="hidden"
            animate="show"
            exit="hidden"
          >
            <GlassCard hover="none" className="p-6">
              {/* Search */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  placeholder="Search for your bank..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-12 rounded-xl"
                />
              </div>

              {/* Bank Grid */}
              <div className="grid grid-cols-2 gap-3 max-h-[320px] overflow-y-auto pr-1">
                {filteredBanks.map((bank) => (
                  <motion.button
                    key={bank.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleBankSelect(bank)}
                    className="flex items-center gap-3 p-4 rounded-xl border border-border bg-card hover:border-primary hover:bg-primary/5 transition-all text-left"
                  >
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
                      style={{ backgroundColor: `${bank.color}20` }}
                    >
                      {bank.logo}
                    </div>
                    <span className="font-medium text-sm">{bank.name}</span>
                  </motion.button>
                ))}
              </div>

              {filteredBanks.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Building2 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No banks found matching "{searchQuery}"</p>
                </div>
              )}

              {/* Security Notice */}
              <div className="flex items-center gap-2 mt-6 p-3 rounded-lg bg-muted/50 text-sm text-muted-foreground">
                <Shield className="w-4 h-4 text-primary flex-shrink-0" />
                <span>Your credentials are encrypted and never stored by Trajectory</span>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Credentials Entry */}
        {state === 'credentials' && selectedBank && (
          <motion.div
            key="credentials"
            variants={scaleIn}
            initial="hidden"
            animate="show"
            exit="hidden"
          >
            <GlassCard hover="none" className="p-6">
              {/* Selected Bank Header */}
              <div className="flex items-center gap-4 mb-6 pb-4 border-b border-border">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                  style={{ backgroundColor: `${selectedBank.color}20` }}
                >
                  {selectedBank.logo}
                </div>
                <div>
                  <h3 className="font-semibold">{selectedBank.name}</h3>
                  <p className="text-sm text-muted-foreground">Enter your online banking credentials</p>
                </div>
              </div>

              {/* Credential Form */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username or Email</Label>
                  <Input
                    id="username"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="h-12 rounded-xl"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="h-12 rounded-xl pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Sandbox Hint */}
                <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 text-sm">
                  <p className="font-medium text-primary mb-1">Sandbox Mode</p>
                  <p className="text-muted-foreground">
                    Use <span className="font-mono bg-muted px-1 rounded">user_good</span> / <span className="font-mono bg-muted px-1 rounded">pass_good</span> for a successful connection
                  </p>
                </div>

                {/* Error Display */}
                {error && (
                  <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
                    {error}
                  </div>
                )}

                <Button
                  onClick={handleSignIn}
                  disabled={!username || !password || isConnecting}
                  className="w-full h-12 rounded-xl"
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Sign In Securely
                </Button>

                <button
                  onClick={handleBackToSearch}
                  className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  ← Choose a different bank
                </button>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Connecting State */}
        {state === 'connecting' && (
          <motion.div
            key="connecting"
            variants={scaleIn}
            initial="hidden"
            animate="show"
            exit="hidden"
          >
            <GlassCard hover="none" className="p-8 text-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-16 h-16 rounded-full border-4 border-primary/30 border-t-primary mx-auto mb-6"
              />
              <h3 className="text-lg font-semibold mb-2">Connecting to {selectedBank?.name}</h3>
              <p className="text-muted-foreground">Securely fetching your account data...</p>
              
              <div className="mt-6 space-y-2 text-sm text-muted-foreground">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span>Credentials verified</span>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.2 }}
                  className="flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span>Retrieving accounts</span>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.9 }}
                  className="flex items-center justify-center gap-2"
                >
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span>Loading transaction history</span>
                </motion.div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Success State */}
        {state === 'success' && (
          <motion.div
            key="success"
            variants={scaleIn}
            initial="hidden"
            animate="show"
            exit="hidden"
          >
            <GlassCard hover="none" className="p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6"
              >
                <CheckCircle2 className="w-10 h-10 text-green-500" />
              </motion.div>
              <h3 className="text-xl font-semibold mb-2">Bank Connected!</h3>
              <p className="text-muted-foreground mb-4">
                Successfully linked your {selectedBank?.name} accounts
              </p>
              <div className="text-sm text-muted-foreground">
                Proceeding to evaluation...
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation - Only show on bank selection */}
      {state === 'select-bank' && (
        <motion.div 
          variants={fadeInUp} 
          className="flex items-center justify-between mt-8"
        >
          <Button variant="outline" onClick={onBack} className="rounded-xl">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="text-sm text-muted-foreground">
            Select a bank to continue
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
