import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { ChurnRiskBar } from "@/components/ChurnRiskBar";
import { SegmentBadge } from "@/components/SegmentBadge";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { useCustomer } from "@/hooks/useCustomer";
import { formatCurrency, formatDate, formatNumber, formatPercent } from "@/lib/utils";

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: customer, isLoading, isError } = useCustomer(id);

  if (isLoading) {
    return (
      <div className="max-w-4xl">
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (isError || !customer) {
    return (
      <EmptyState
        title="Customer not found"
        description="The customer may have been removed or the ID is invalid."
        actionLabel="Back to customers"
        onAction={() => window.history.back()}
      />
    );
  }

  return (
    <div>
      <PageHeader
        title={customer.external_id}
        description={`Member since ${formatDate(customer.created_at)}`}
        actions={
          <Link to="/customers">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </Link>
        }
      />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-6">
            <h3 className="text-sm font-semibold text-slate-300">Profile</h3>
            <dl className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Region" value={customer.region ?? "—"} />
              <Field label="Gender" value={customer.gender ?? "—"} />
              <Field label="Age" value={customer.age?.toString() ?? "—"} />
              <Field label="Membership" value={customer.membership_status} />
              <Field label="Value tier" value={customer.value_tier ?? "—"} />
              <Field label="Preferred category" value={customer.preferred_category ?? "—"} />
            </dl>
          </section>
          <section className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-6">
            <h3 className="text-sm font-semibold text-slate-300">Transactions</h3>
            {customer.transactions.length ? (
              <table className="mt-4 w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-500">
                    <th className="pb-2">Date</th>
                    <th className="pb-2">Category</th>
                    <th className="pb-2">Channel</th>
                    <th className="pb-2 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {customer.transactions.map((tx) => (
                    <tr key={tx.id} className="border-t border-slate-800">
                      <td className="py-2 text-slate-300">{formatDate(tx.transaction_date)}</td>
                      <td className="py-2 text-slate-300">{tx.category ?? "—"}</td>
                      <td className="py-2 text-slate-400">{tx.channel ?? "—"}</td>
                      <td className="py-2 text-right text-slate-100">
                        {formatCurrency(Number(tx.amount))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="mt-4 text-sm text-slate-500">No transactions recorded</p>
            )}
          </section>
        </div>
        <div className="space-y-6">
          {customer.segment ? (
            <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-6">
              <h3 className="text-sm font-semibold text-slate-300">Segment</h3>
              <div className="mt-3">
                <SegmentBadge
                  name={customer.segment.name}
                  color={customer.segment.color_hex}
                  size="md"
                />
              </div>
              <p className="mt-2 text-sm text-slate-400">{customer.segment.description}</p>
            </div>
          ) : null}
          <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-6">
            <h3 className="text-sm font-semibold text-slate-300">Metrics</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <Field label="Total spend" value={formatCurrency(Number(customer.total_spend))} />
              <Field label="CLV estimate" value={formatCurrency(Number(customer.clv_estimate))} />
              <Field label="RFM score" value={customer.rfm_score?.toString() ?? "—"} />
              <Field
                label="Engagement"
                value={formatPercent(Number(customer.engagement_index))}
              />
              <Field label="Orders" value={formatNumber(customer.purchase_frequency)} />
            </dl>
            <div className="mt-4">
              <p className="mb-2 text-xs text-slate-500">Churn probability</p>
              <ChurnRiskBar probability={Number(customer.churn_probability)} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="mt-0.5 font-medium text-slate-100">{value}</dd>
    </div>
  );
}