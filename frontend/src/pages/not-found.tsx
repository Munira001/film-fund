import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-background p-6 text-foreground">
      <Card className="w-full max-w-md mx-4">
        <CardContent className="pt-6">
          <div className="mb-4 flex gap-2">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <h1 className="display text-2xl font-medium tracking-[-0.5px]">
              404 Page Not Found
            </h1>
          </div>

          <p className="mt-4 text-sm text-muted-foreground">
            That page is not in this workspace.
          </p>
          <Link
            to="/"
            className="mt-6 inline-flex text-sm font-medium text-brand hover:underline"
          >
            Back to FILMFUND
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
