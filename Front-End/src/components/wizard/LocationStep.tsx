/**
 * Location Step
 * 
 * Step for selecting business location using Google Maps Places Autocomplete.
 * Uses Google Maps API, Places API, and Geocode API.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Search, ArrowLeft, ArrowRight, Loader2, X, Navigation } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { GlassCard } from '@/components/ui/GlassCard';
import { staggerContainer, fadeInUp, buttonHover } from '@/lib/animations';
import type { LocationDetails } from '@/types';

interface LocationStepProps {
  initialLocation?: LocationDetails;
  onSubmit: (location: LocationDetails) => void;
  onBack: () => void;
}

interface PlacePrediction {
  place_id: string;
  description: string;
  structured_formatting: {
    main_text: string;
    secondary_text: string;
  };
}

export function LocationStep({ initialLocation, onSubmit, onBack }: LocationStepProps) {
  const [searchQuery, setSearchQuery] = useState(initialLocation?.formattedAddress || '');
  const [predictions, setPredictions] = useState<PlacePrediction[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationDetails | null>(initialLocation || null);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isGettingCurrentLocation, setIsGettingCurrentLocation] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Simulated place search (will be replaced with actual Google API call)
  const searchPlaces = useCallback(async (query: string) => {
    if (query.length < 3) {
      setPredictions([]);
      return;
    }

    setIsSearching(true);
    
    // Simulate API delay - Replace with actual Google Places Autocomplete API call
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Mock predictions - These would come from Google Places API
    const mockPredictions: PlacePrediction[] = [
      {
        place_id: 'ChIJN1t_tDeuEmsRUsoyG83frY4',
        description: `${query}, New York, NY, USA`,
        structured_formatting: {
          main_text: query,
          secondary_text: 'New York, NY, USA'
        }
      },
      {
        place_id: 'ChIJIQBpAG2ahYAR_6128GcTUEo',
        description: `${query}, San Francisco, CA, USA`,
        structured_formatting: {
          main_text: query,
          secondary_text: 'San Francisco, CA, USA'
        }
      },
      {
        place_id: 'ChIJE9on3F3HwoAR9AhGJW_fL-I',
        description: `${query}, Los Angeles, CA, USA`,
        structured_formatting: {
          main_text: query,
          secondary_text: 'Los Angeles, CA, USA'
        }
      },
    ];
    
    setPredictions(mockPredictions);
    setShowDropdown(true);
    setIsSearching(false);
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery && !selectedLocation) {
        searchPlaces(searchQuery);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedLocation, searchPlaces]);

  // Handle place selection - would call Geocode API for details
  const handleSelectPlace = async (prediction: PlacePrediction) => {
    setIsSearching(true);
    setShowDropdown(false);
    
    // Simulate Geocode API call
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Mock geocoded data - Replace with actual Google Geocode API response
    const locationDetails: LocationDetails = {
      formattedAddress: prediction.description,
      placeId: prediction.place_id,
      coordinates: {
        lat: 40.7128 + Math.random() * 0.1, // Mock coordinates
        lng: -74.0060 + Math.random() * 0.1,
      },
      city: prediction.structured_formatting.secondary_text.split(',')[0],
      state: prediction.structured_formatting.secondary_text.split(',')[1]?.trim(),
      country: 'USA',
      postalCode: '10001', // Would come from Geocode API
    };
    
    setSelectedLocation(locationDetails);
    setSearchQuery(prediction.description);
    setPredictions([]);
    setIsSearching(false);
  };

  // Get current location using browser geolocation
  const handleGetCurrentLocation = async () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    setIsGettingCurrentLocation(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        // Simulate reverse geocoding - Replace with actual Google Geocode API
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const locationDetails: LocationDetails = {
          formattedAddress: '123 Current Street, Your City, State, USA',
          coordinates: {
            lat: latitude,
            lng: longitude,
          },
          city: 'Your City',
          state: 'State',
          country: 'USA',
          postalCode: '12345',
        };
        
        setSelectedLocation(locationDetails);
        setSearchQuery(locationDetails.formattedAddress);
        setIsGettingCurrentLocation(false);
      },
      (error) => {
        console.error('Error getting location:', error);
        setIsGettingCurrentLocation(false);
        alert('Unable to get your location. Please search manually.');
      }
    );
  };

  const handleClearSelection = () => {
    setSelectedLocation(null);
    setSearchQuery('');
    setPredictions([]);
    inputRef.current?.focus();
  };

  const handleSubmit = () => {
    if (selectedLocation) {
      onSubmit(selectedLocation);
    }
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="max-w-2xl mx-auto"
    >
      <motion.div variants={fadeInUp} className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Business Location</h2>
        <p className="text-muted-foreground">
          Search for your business address to help us verify your location
        </p>
      </motion.div>

      <GlassCard hover="none" className="p-8">
        <div className="space-y-6">
          {/* Search Input */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <Label htmlFor="location" className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-primary" />
              Search Address
            </Label>
            <div className="relative" ref={dropdownRef}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  ref={inputRef}
                  id="location"
                  placeholder="Start typing an address..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    if (selectedLocation) {
                      setSelectedLocation(null);
                    }
                  }}
                  onFocus={() => {
                    if (predictions.length > 0) {
                      setShowDropdown(true);
                    }
                  }}
                  className="pl-10 pr-10"
                />
                {isSearching && (
                  <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-muted-foreground" />
                )}
                {selectedLocation && !isSearching && (
                  <button
                    type="button"
                    onClick={handleClearSelection}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Predictions Dropdown */}
              {showDropdown && predictions.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute z-50 w-full mt-1 bg-background border border-border rounded-lg shadow-lg overflow-hidden"
                >
                  {predictions.map((prediction) => (
                    <button
                      key={prediction.place_id}
                      type="button"
                      onClick={() => handleSelectPlace(prediction)}
                      className="w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors border-b border-border last:border-b-0"
                    >
                      <div className="font-medium text-sm">
                        {prediction.structured_formatting.main_text}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {prediction.structured_formatting.secondary_text}
                      </div>
                    </button>
                  ))}
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Use Current Location Button */}
          <motion.div variants={fadeInUp}>
            <Button
              type="button"
              variant="outline"
              onClick={handleGetCurrentLocation}
              disabled={isGettingCurrentLocation}
              className="w-full"
            >
              {isGettingCurrentLocation ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Navigation className="w-4 h-4 mr-2" />
              )}
              Use My Current Location
            </Button>
          </motion.div>

          {/* Selected Location Display */}
          {selectedLocation && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 rounded-lg bg-primary/5 border border-primary/20"
            >
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-foreground">
                    {selectedLocation.formattedAddress}
                  </p>
                  {selectedLocation.coordinates && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Coordinates: {selectedLocation.coordinates.lat.toFixed(4)}, {selectedLocation.coordinates.lng.toFixed(4)}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Map Preview Placeholder */}
          <motion.div variants={fadeInUp}>
            <div className="h-48 rounded-lg bg-muted/30 border border-border flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">
                  {selectedLocation 
                    ? 'Map preview will appear here' 
                    : 'Search for an address to see it on the map'}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Navigation Buttons */}
          <motion.div variants={fadeInUp} className="flex gap-4 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              className="flex-1"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <motion.div
              variants={buttonHover}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
              className="flex-1"
            >
              <Button
                type="button"
                onClick={handleSubmit}
                disabled={!selectedLocation}
                className="w-full"
              >
                Continue to Bank Data
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </GlassCard>
    </motion.div>
  );
}
