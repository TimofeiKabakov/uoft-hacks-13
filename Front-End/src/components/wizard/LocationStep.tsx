/**
 * Location Step
 * 
 * Step for selecting business location using Google Maps Places Autocomplete.
 * Uses Google Maps API, Places API, and Geocode API.
 */

import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
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
  const [searchError, setSearchError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const googleApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const sessionToken = useMemo(
    () => (crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)),
    []
  );

  const parseAddressComponents = (components: any[] = []) => {
    const get = (type: string) => components.find((c) => c.types?.includes(type))?.long_name;
    return {
      city: get('locality') || get('sublocality') || '',
      state: get('administrative_area_level_1') || '',
      country: get('country') || '',
      postalCode: get('postal_code') || '',
    };
  };

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

  // Google Places autocomplete search (fallback to mock if no key)
  const searchPlaces = useCallback(async (query: string) => {
    if (query.length < 3) {
      setPredictions([]);
      return;
    }

    setIsSearching(true);
    setSearchError(null);

    if (!googleApiKey) {
      const mockPredictions: PlacePrediction[] = [
        {
          place_id: 'mock-1',
          description: `${query} (mock), New York, NY, USA`,
          structured_formatting: { main_text: query, secondary_text: 'New York, NY, USA' }
        },
        {
          place_id: 'mock-2',
          description: `${query} (mock), San Francisco, CA, USA`,
          structured_formatting: { main_text: query, secondary_text: 'San Francisco, CA, USA' }
        },
      ];
      setPredictions(mockPredictions);
      setShowDropdown(true);
      setIsSearching(false);
      setSearchError('Add VITE_GOOGLE_MAPS_API_KEY to enable full Google results.');
      return;
    }

    try {
      const resp = await fetch(
        `https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${encodeURIComponent(
          query
        )}&types=address&key=${googleApiKey}&sessiontoken=${sessionToken}`
      );
      const data = await resp.json();
      if (data.status !== 'OK') {
        setSearchError(`Places API error: ${data.status}`);
        setPredictions([]);
      } else {
        setPredictions(
          (data.predictions || []).map((p: any) => ({
            place_id: p.place_id,
            description: p.description,
            structured_formatting: p.structured_formatting,
          }))
        );
        setShowDropdown(true);
      }
    } catch (error) {
      console.error('Error fetching places:', error);
      setSearchError('Unable to fetch places right now.');
      setPredictions([]);
    } finally {
      setIsSearching(false);
    }
  }, [googleApiKey, sessionToken]);

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

    if (!googleApiKey) {
      const locationDetails: LocationDetails = {
        formattedAddress: prediction.description,
        placeId: prediction.place_id,
        coordinates: {
          lat: 40.7128 + Math.random() * 0.1,
          lng: -74.0060 + Math.random() * 0.1,
        },
        city: prediction.structured_formatting.secondary_text.split(',')[0],
        state: prediction.structured_formatting.secondary_text.split(',')[1]?.trim(),
        country: 'USA',
        postalCode: '10001',
      };
      setSelectedLocation(locationDetails);
      setSearchQuery(prediction.description);
      setPredictions([]);
      setIsSearching(false);
      return;
    }

    try {
      const detailsResp = await fetch(
        `https://maps.googleapis.com/maps/api/place/details/json?placeid=${prediction.place_id}&fields=formatted_address,geometry,address_components&key=${googleApiKey}&sessiontoken=${sessionToken}`
      );
      const details = await detailsResp.json();

      if (details.status !== 'OK') {
        setSearchError(`Place details error: ${details.status}`);
        setIsSearching(false);
        return;
      }

      const components = parseAddressComponents(details.result.address_components);
      const coords = details.result.geometry?.location;

      const locationDetails: LocationDetails = {
        formattedAddress: details.result.formatted_address,
        placeId: prediction.place_id,
        coordinates: coords ? { lat: Number(coords.lat), lng: Number(coords.lng) } : undefined,
        city: components.city,
        state: components.state,
        country: components.country,
        postalCode: components.postalCode,
      };

      setSelectedLocation(locationDetails);
      setSearchQuery(details.result.formatted_address);
      setPredictions([]);
    } catch (error) {
      console.error('Error fetching place details:', error);
      setSearchError('Unable to fetch place details right now.');
    } finally {
      setIsSearching(false);
    }
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
        
        try {
          if (googleApiKey) {
            const resp = await fetch(
              `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${googleApiKey}`
            );
            const data = await resp.json();
            const first = data.results?.[0];
            const components = parseAddressComponents(first?.address_components);

            const locationDetails: LocationDetails = {
              formattedAddress: first?.formatted_address || 'Current location',
              coordinates: { lat: latitude, lng: longitude },
              city: components.city,
              state: components.state,
              country: components.country,
              postalCode: components.postalCode,
            };

            setSelectedLocation(locationDetails);
            setSearchQuery(locationDetails.formattedAddress);
          } else {
            const locationDetails: LocationDetails = {
              formattedAddress: 'Current location (mock)',
              coordinates: { lat: latitude, lng: longitude },
            };
            setSelectedLocation(locationDetails);
            setSearchQuery(locationDetails.formattedAddress);
          }
        } catch (error) {
          console.error('Error reverse geocoding:', error);
          alert('Unable to reverse geocode your location.');
        } finally {
          setIsGettingCurrentLocation(false);
        }
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
          {searchError && (
            <p className="text-xs text-destructive">{searchError}</p>
          )}

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
