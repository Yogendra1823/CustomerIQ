import { useState } from "react";
import { Brain, Play } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { TableSkeleton } from "@/components/LoadingSkeleton";
import { EmptyState } from "@/components/EmptyState";
import { useML } from "@/hooks/useML";
import { formatDate, formatNumber } from "@/lib/utils";

export function MLStudioPage() {
  const { data: models = [], isLoading, trainModel } = useML();
  const [algorithm, setAlgorithm] = useState("kmeans");
  const [clusters, setClusters] = useState(5);

  const handleTrain = () => {
    void trainModel.mutateAsync({
      algorithm,
      n_clusters: clusters,
      run_name: `${algorithm}-${clusters}-${Date.now()}`,
    });
  };

  return (
    <div>
      <PageHeader
        title="ML Studio"
        description="Train and manage clustering models for segmentation"
      />
      <div className="mb-6 rounded-xl border border-slate-700/60 bg-slate-900/50 p-6">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-300">
          <Brain className="h-4 w-4 text-cyan-400" />
          Train new model
        </h3>
        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div>
            <label className="text-xs text-slate-500">Algorithm</label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="mt-1 block h-10 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-200"
            >
              <option value="kmeans">K-Means</option>
              <option value="gmm">Gaussian Mixture</option>
              <option value="hierarchical">Hierarchical</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-500">Clusters (k)</label>
            <input
              type="number"
              min={2}
              max={20}
              value={clusters}
              onChange={(e) => setClusters(Number(e.target.value))}
              className="mt-1 block h-10 w-24 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-200"
            />
          </div>
          <Button onClick={handleTrain} isLoading={trainModel.isPending}>
            <Play className="h-4 w-4" />
            Start training
          </Button>
        </div>
        {trainModel.isSuccess ? (
          <p className="mt-3 text-sm text-emerald-400">
            Training started — run {trainModel.data?.data.run_id}
          </p>
        ) : null}
        {trainModel.isError ? (
          <p className="mt-3 text-sm text-red-400">Training failed. Check API connection.</p>
        ) : null}
      </div>
      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : models.length === 0 ? (
        <EmptyState
          title="No models yet"
          description="Train your first clustering model to auto-generate segments."
          actionLabel="Train model"
          onAction={handleTrain}
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-700/60">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900/80 text-left text-xs uppercase text-slate-500">
                <th className="px-4 py-3">Run</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">k</th>
                <th className="px-4 py-3">Silhouette</th>
                <th className="px-4 py-3">Samples</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id} className="border-b border-slate-800/80">
                  <td className="px-4 py-3 font-medium text-cyan-400">
                    {m.run_name ?? m.id.slice(0, 8)}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{m.algorithm ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-300">{m.n_clusters ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-300">
                    {m.silhouette_score != null ? Number(m.silhouette_score).toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {formatNumber(m.training_samples)}
                  </td>
                  <td className="px-4 py-3">
                    {m.is_active ? (
                      <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-400">
                        Active
                      </span>
                    ) : (
                      <span className="text-slate-500">Inactive</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-400">{formatDate(m.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}