import { PageHeader } from '@/components/common/page-header';
import { SectionCard } from '@/components/common/section-card';
import { EmptyState } from '@/components/common/empty-state';

export default function UploadPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Upload" description="Manage upload tasks and settings." />
      <SectionCard>
        <EmptyState title="Coming Soon" description="The upload module is under development." />
      </SectionCard>
    </div>
  );
}
