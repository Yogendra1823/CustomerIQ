import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { ChurnRiskBar } from "@/components/ChurnRiskBar";
import { SegmentBadge } from "@/components/SegmentBadge";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { useCustomer } from "@/hooks/useCustomer";
import { formatCurrency, formatDate, formatNumber } from "@/lib/utils";

interface CustomerDrawerProps {
  customerId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CustomerDrawer({ customerId, open, onOpenChange }: CustomerDrawerProps) {
  const { data: customer, isLoading } = useCustomer(customerId ?? undefined);

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" />
        <Dialog.Content className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-slate-700 bg-slate-950 shadow-2xl focus:outline-none">
          <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
            <Dialog.Title className="text-lg font-semibold text-slate-100">
              Customer preview
            </Dialog.Title>
            <Dialog.Close className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white">
              <X className="h-5 w-5" />
            </Dialog.Close>
          </div>
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {isLoading ? (
              <LoadingSkeleton rows={6} />
            ) : customer ? (
              <div className="space-y-6">
                <div>
                  <p className="text-xs text-slate-500">External ID</p>
                  <p className="text-xl font-bold text-cyan-400">{customer.external_id}</p>
                  {customer.segment ? (
                    <div className="mt-2">
                      <SegmentBadge
                        name={customer.segment.name}
                        color={customer.segment.color_hex}
                      />
                    </div>
                  ) : null}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Stat label="Total spend" value={formatCurrency(Number(customer.total_spend))} />
                  <Stat label="CLV estimate" value={formatCurrency(Number(customer.clv_estimate))} />
                  <Stat label="Orders" value={formatNumber(customer.purchase_frequency)} />
                  <Stat label="Region" value={customer.region ?? "—"} />
                </div>
                <div>
                  <p className="mb-2 text-xs font-medium uppercase text-slate-500">Churn risk</p>
                  <ChurnRiskBar probability={Number(customer.churn_probability)} />
                </div>
                <div>
                  <p className="mb-2 text-xs font-medium uppercase text-slate-500">
                    Recent transactions
                  </p>
                  {customer.transactions.length ? (
                    <ul className="space-y-2">
                      {customer.transactions.slice(0, 5).map((tx) => (
                        <li
                          key={tx.id}
                          className="flex justify-between rounded-lg bg-slate-900 px-3 py-2 text-sm"
                        >
                          <span className="text-slate-300">{tx.category ?? tx.order_id}</span>
                          <span className="text-slate-100">
                            {formatCurrency(Number(tx.amount))}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-slate-500">No transactions</p>
                  )}
                </div>
                <p className="text-xs text-slate-600">
                  Joined {formatDate(customer.created_at)}
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Customer not found</p>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-900/80 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}