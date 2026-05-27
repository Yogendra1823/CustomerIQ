import { useState } from "react";
import { Plus } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import * as Dialog from "@radix-ui/react-dialog";
import { SegmentBadge } from "@/components/SegmentBadge";
import { EmptyState } from "@/components/EmptyState";
import { CardSkeleton } from "@/components/LoadingSkeleton";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { useSegments } from "@/hooks/useSegments";
import { formatCurrency, formatPercent, slugify } from "@/lib/utils";

const schema = z.object({
  name: z.string().min(2, "Name required"),
  slug: z.string().min(2, "Slug required"),
  description: z.string().optional(),
  color_hex: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export function SegmentsPage() {
  const { data: segments = [], isLoading, createSegment } = useSegments();
  const [open, setOpen] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", slug: "", description: "", color_hex: "#22d3ee" },
  });

  const name = watch("name");

  const onSubmit = async (data: FormData) => {
    await createSegment.mutateAsync({
      name: data.name,
      slug: data.slug || slugify(data.name),
      description: data.description ?? null,
      color_hex: data.color_hex ?? null,
    });
    reset();
    setOpen(false);
  };

  return (
    <div>
      <PageHeader
        title="Segments"
        description="Customer segments with CLV and churn benchmarks"
        actions={
          <Button onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" />
            New segment
          </Button>
        }
      />
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : segments.length === 0 ? (
        <EmptyState
          title="No segments yet"
          description="Create your first segment or run ML clustering in ML Studio."
          actionLabel="Create segment"
          onAction={() => setOpen(true)}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {segments.map((seg) => (
            <article
              key={seg.id}
              className="rounded-xl border border-slate-700/60 bg-gradient-to-br from-slate-900 to-slate-950 p-5"
            >
              <SegmentBadge name={seg.name} color={seg.color_hex} size="md" />
              <p className="mt-3 text-sm text-slate-400 line-clamp-2">
                {seg.description ?? "No description"}
              </p>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <dt className="text-slate-500">Size</dt>
                  <dd className="font-semibold text-slate-200">{seg.size ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Avg CLV</dt>
                  <dd className="font-semibold text-slate-200">
                    {formatCurrency(Number(seg.avg_clv))}
                  </dd>
                </div>
                <div>
                  <dt className="text-slate-500">Churn</dt>
                  <dd className="font-semibold text-slate-200">
                    {formatPercent(Number(seg.churn_rate))}
                  </dd>
                </div>
                <div>
                  <dt className="text-slate-500">Revenue share</dt>
                  <dd className="font-semibold text-slate-200">
                    {formatPercent(Number(seg.revenue_share))}
                  </dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      )}
      <Dialog.Root open={open} onOpenChange={setOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border border-slate-700 bg-slate-900 p-6 shadow-xl focus:outline-none">
            <Dialog.Title className="text-lg font-semibold text-slate-100">
              Create segment
            </Dialog.Title>
            <form
              onSubmit={(e) => {
                setValue("slug", slugify(name || ""));
                void handleSubmit(onSubmit)(e);
              }}
              className="mt-4 space-y-4"
            >
              <div>
                <label className="text-xs text-slate-400">Name</label>
                <input
                  {...register("name")}
                  onBlur={() => setValue("slug", slugify(name || ""))}
                  className="mt-1 h-10 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100"
                />
                {errors.name ? (
                  <p className="mt-1 text-xs text-red-400">{errors.name.message}</p>
                ) : null}
              </div>
              <div>
                <label className="text-xs text-slate-400">Slug</label>
                <input
                  {...register("slug")}
                  className="mt-1 h-10 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400">Description</label>
                <textarea
                  {...register("description")}
                  rows={3}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400">Color</label>
                <input
                  type="color"
                  {...register("color_hex")}
                  className="mt-1 h-10 w-full cursor-pointer rounded-lg border border-slate-700 bg-slate-950"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" isLoading={createSegment.isPending}>
                  Create
                </Button>
              </div>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}