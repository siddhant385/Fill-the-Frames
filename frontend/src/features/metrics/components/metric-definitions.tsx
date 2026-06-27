import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BookOpen } from 'lucide-react';

export function MetricDefinitions() {
  const definitions = [
    { name: 'SSIM', title: 'Structural Similarity Index', desc: 'Measures the similarity between two images. Higher is better (max 1.0). Focuses on structural coherence rather than absolute pixel errors.' },
    { name: 'PSNR', title: 'Peak Signal-to-Noise Ratio', desc: 'Ratio between the maximum possible power of a signal and the power of corrupting noise (MSE). Higher is better.' },
    { name: 'Accuracy', title: 'Validation Accuracy', desc: 'Overall accuracy percentage derived from structural and signal validation metrics.' },
  ];

  return (
    <Card className="bg-muted/10">
      <CardHeader className="pb-3 border-b">
        <CardTitle className="text-md flex items-center gap-2 text-muted-foreground uppercase tracking-wider">
          <BookOpen className="w-5 h-5" />
          Metric Definitions Reference
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <dl className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {definitions.map((def) => (
            <div key={def.name} className="flex flex-col gap-1">
              <dt className="font-semibold flex items-baseline gap-2">
                <span className="text-primary">{def.name}</span>
                <span className="text-xs text-muted-foreground font-normal">{def.title}</span>
              </dt>
              <dd className="text-xs text-muted-foreground leading-relaxed mt-1">
                {def.desc}
              </dd>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
}
