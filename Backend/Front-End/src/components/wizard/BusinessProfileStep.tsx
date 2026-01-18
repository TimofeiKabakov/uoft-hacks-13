/**
 * Business Profile Step
 * 
 * Step 1: Collect business information and employment details with validation.
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Building2, MapPin, Tag, ArrowRight, Briefcase, DollarSign, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GlassCard } from '@/components/ui/GlassCard';
import { Separator } from '@/components/ui/separator';
import { staggerContainer, fadeInUp, buttonHover } from '@/lib/animations';
import type { BusinessProfile } from '@/types';

// Validation schema
const businessProfileSchema = z.object({
  businessName: z.string()
    .trim()
    .min(2, 'Business name must be at least 2 characters')
    .max(100, 'Business name must be less than 100 characters'),
  businessType: z.string()
    .min(1, 'Please select a business type'),
  zipCode: z.string()
    .trim()
    .regex(/^\d{5}(-\d{4})?$/, 'Please enter a valid ZIP code'),
  address: z.string()
    .trim()
    .max(200, 'Address must be less than 200 characters')
    .optional(),
  communityTags: z.string()
    .max(500, 'Tags must be less than 500 characters')
    .optional(),
  // Employment details
  employmentStatus: z.string()
    .min(1, 'Please select your employment status'),
  employer: z.string()
    .trim()
    .max(100, 'Employer name must be less than 100 characters')
    .optional(),
  jobTitle: z.string()
    .trim()
    .max(100, 'Job title must be less than 100 characters')
    .optional(),
  monthlyIncome: z.string()
    .optional()
    .transform(val => val ? parseFloat(val) : undefined)
    .pipe(z.number().min(0, 'Income must be positive').optional()),
  yearsAtCurrentJob: z.string()
    .optional()
    .transform(val => val ? parseFloat(val) : undefined)
    .pipe(z.number().min(0, 'Years must be positive').max(50, 'Please enter a valid number').optional()),
});

type FormData = z.infer<typeof businessProfileSchema>;
type FormInput = z.input<typeof businessProfileSchema>;

interface BusinessProfileStepProps {
  initialData?: Partial<BusinessProfile>;
  onSubmit: (data: Partial<BusinessProfile>) => void;
}

const businessTypes = [
  { value: 'restaurant', label: 'Restaurant / Food Service' },
  { value: 'retail', label: 'Retail Store' },
  { value: 'services', label: 'Professional Services' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'technology', label: 'Technology' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'nonprofit', label: 'Nonprofit Organization' },
  { value: 'other', label: 'Other' },
];

const employmentStatuses = [
  { value: 'employed', label: 'Employed (Full-time/Part-time)' },
  { value: 'self-employed', label: 'Self-Employed' },
  { value: 'business-owner', label: 'Business Owner' },
  { value: 'unemployed', label: 'Currently Unemployed' },
  { value: 'retired', label: 'Retired' },
];

export function BusinessProfileStep({ initialData, onSubmit }: BusinessProfileStepProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    watch,
  } = useForm<FormInput, unknown, FormData>({
    resolver: zodResolver(businessProfileSchema),
    mode: 'onChange',
    defaultValues: {
      businessName: initialData?.businessName || '',
      businessType: initialData?.businessType || '',
      zipCode: initialData?.location?.zipCode || '',
      address: initialData?.location?.address || '',
      communityTags: initialData?.communityTags?.join(', ') || '',
      employmentStatus: initialData?.employmentDetails?.employmentStatus || '',
      employer: initialData?.employmentDetails?.employer || '',
      jobTitle: initialData?.employmentDetails?.jobTitle || '',
      monthlyIncome: initialData?.employmentDetails?.monthlyIncome?.toString() || '',
      yearsAtCurrentJob: initialData?.employmentDetails?.yearsAtCurrentJob?.toString() || '',
    },
  });

  const businessType = watch('businessType');
  const employmentStatus = watch('employmentStatus');
  const showEmployerFields = employmentStatus === 'employed';

  const onFormSubmit = (data: FormData) => {
    const profile: Partial<BusinessProfile> = {
      businessName: data.businessName,
      businessType: data.businessType,
      location: {
        zipCode: data.zipCode,
        address: data.address,
      },
      communityTags: data.communityTags 
        ? data.communityTags.split(',').map(tag => tag.trim()).filter(Boolean)
        : [],
      employmentDetails: {
        employmentStatus: data.employmentStatus as BusinessProfile['employmentDetails']['employmentStatus'],
        employer: data.employer,
        jobTitle: data.jobTitle,
        monthlyIncome: data.monthlyIncome,
        yearsAtCurrentJob: data.yearsAtCurrentJob,
      },
    };
    onSubmit(profile);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="max-w-2xl mx-auto"
    >
      <motion.div variants={fadeInUp} className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Business Profile</h2>
        <p className="text-muted-foreground">
          Tell us about your business to begin the evaluation
        </p>
      </motion.div>

      <GlassCard hover="none" className="p-8">
        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
          {/* Business Name */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <Label htmlFor="businessName" className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-primary" />
              Business Name
            </Label>
            <Input
              id="businessName"
              placeholder="Enter your business name"
              {...register('businessName')}
              className={errors.businessName ? 'border-destructive' : ''}
            />
            {errors.businessName && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-destructive"
              >
                {errors.businessName.message}
              </motion.p>
            )}
          </motion.div>

          {/* Business Type */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <Label htmlFor="businessType" className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-primary" />
              Business Type
            </Label>
            <Select
              value={businessType}
              onValueChange={(value) => setValue('businessType', value, { shouldValidate: true })}
            >
              <SelectTrigger className={errors.businessType ? 'border-destructive' : ''}>
                <SelectValue placeholder="Select business type" />
              </SelectTrigger>
              <SelectContent>
                {businessTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.businessType && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-destructive"
              >
                {errors.businessType.message}
              </motion.p>
            )}
          </motion.div>

          {/* Location */}
          <motion.div variants={fadeInUp} className="space-y-4">
            <Label className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-primary" />
              Location
            </Label>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Input
                  placeholder="ZIP Code"
                  {...register('zipCode')}
                  className={errors.zipCode ? 'border-destructive' : ''}
                />
                {errors.zipCode && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-destructive"
                  >
                    {errors.zipCode.message}
                  </motion.p>
                )}
              </div>
              <div>
                <Input
                  placeholder="Street address (optional)"
                  {...register('address')}
                />
              </div>
            </div>
          </motion.div>

          {/* Community Tags */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <Label htmlFor="communityTags" className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-accent" />
              Community Context <span className="text-muted-foreground text-xs">(optional)</span>
            </Label>
            <Input
              id="communityTags"
              placeholder="e.g., minority-owned, veteran-owned, women-led"
              {...register('communityTags')}
            />
            <p className="text-xs text-muted-foreground">
              Separate multiple tags with commas
            </p>
          </motion.div>

          {/* Separator */}
          <motion.div variants={fadeInUp}>
            <Separator className="my-6" />
          </motion.div>

          {/* Employment Details Section */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-primary" />
              Employment Details
            </h3>
            <p className="text-sm text-muted-foreground">
              Help us understand your income sources
            </p>
          </motion.div>

          {/* Employment Status */}
          <motion.div variants={fadeInUp} className="space-y-2">
            <Label htmlFor="employmentStatus" className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-primary" />
              Employment Status
            </Label>
            <Select
              value={employmentStatus}
              onValueChange={(value) => setValue('employmentStatus', value, { shouldValidate: true })}
            >
              <SelectTrigger className={errors.employmentStatus ? 'border-destructive' : ''}>
                <SelectValue placeholder="Select your employment status" />
              </SelectTrigger>
              <SelectContent>
                {employmentStatuses.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.employmentStatus && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-destructive"
              >
                {errors.employmentStatus.message}
              </motion.p>
            )}
          </motion.div>

          {/* Conditional Employer Fields */}
          {showEmployerFields && (
            <>
              <motion.div 
                variants={fadeInUp} 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="grid grid-cols-2 gap-4"
              >
                <div className="space-y-2">
                  <Label htmlFor="employer">Employer Name</Label>
                  <Input
                    id="employer"
                    placeholder="Company name"
                    {...register('employer')}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="jobTitle">Job Title</Label>
                  <Input
                    id="jobTitle"
                    placeholder="Your position"
                    {...register('jobTitle')}
                  />
                </div>
              </motion.div>
            </>
          )}

          {/* Income and Years */}
          <motion.div variants={fadeInUp} className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="monthlyIncome" className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-primary" />
                Monthly Income <span className="text-muted-foreground text-xs">(optional)</span>
              </Label>
              <Input
                id="monthlyIncome"
                type="number"
                placeholder="0.00"
                {...register('monthlyIncome')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="yearsAtCurrentJob" className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                Years at Job <span className="text-muted-foreground text-xs">(optional)</span>
              </Label>
              <Input
                id="yearsAtCurrentJob"
                type="number"
                step="0.5"
                placeholder="0"
                {...register('yearsAtCurrentJob')}
              />
            </div>
          </motion.div>

          {/* Submit */}
          <motion.div variants={fadeInUp} className="pt-4">
            <motion.div
              variants={buttonHover}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
            >
              <Button 
                type="submit" 
                className="w-full rounded-xl py-6 text-lg font-semibold"
                disabled={!isValid}
              >
                Continue to Location
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </motion.div>
          </motion.div>
        </form>
      </GlassCard>
    </motion.div>
  );
}
