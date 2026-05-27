import { useMemo, useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { CustomerDrawer } from "@/components/CustomerDrawer";
import { ChurnRiskBar } from "@/components/ChurnRiskBar";
import { DataTable, type Column } from "@/components/DataTable";
import { FilterPanel } from "@/components/FilterPanel";
import { SegmentBadge } from "@/components/SegmentBadge";
import { TableSkeleton } from "@/components/LoadingSkeleton";
import { PageHeader } from "@/components/layout/PageHeader";
import { useCustomers } from "@/hooks/useCustomers";
import { useSegments } from "@/hooks/useSegments";
import type { Customer } from "@/types";
import { formatCurrency } from "@/lib/utils";

export function CustomersPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get("search") || "";
  
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState(initialSearch);
  const [region, setRegion] = useState("");
  const [valueTier, setValueTier] = useState("");

  // Sync state if URL changes (e.g. from TopBar search)
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    if (urlSearch !== search) {
      setSearch(urlSearch);
      setPage(1);
    }
  }, [searchParams]);

  const updateSearch = (v: string) => {
    setSearch(v);
    setPage(1);
    if (v) {
      setSearchParams({ search: v }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  };

  const [drawerId, setDrawerId] = useState<string | null>(null);

  const { data, isLoading } = useCustomers({
    page,
    limit: 20,
    search: search || undefined,
    region: region || undefined,
    value_tier: valueTier || undefined,
  });
  const { data: segments = [] } = useSegments();

  const segmentMap = useMemo(
    () => new Map(segments.map((s) => [s.id, s])),
    [segments],
  );

  const columns: Column<Customer>[] = [
    {
      key: "external_id",
      header: "Customer ID",
      render: (row) => (
        <span className="font-medium text-cyan-400">{row.external_id}</span>
      ),
    },
    {
      key: "region",
      header: "Region",
      render: (row) => row.region ?? "—",
    },
    {
      key: "value_tier",
      header: "Tier",
      render: (row) => row.value_tier ?? "—",
    },
    {
      key: "total_spend",
      header: "Spend",
      render: (row) => formatCurrency(Number(row.total_spend)),
    },
    {
      key: "churn_probability",
      header: "Churn",
      render: (row) => (
        <div className="w-28">
          <ChurnRiskBar probability={Number(row.churn_probability)} showLabel={false} />
        </div>
      ),
    },
    {
      key: "segment_id",
      header: "Segment",
      render: (row) => {
        const seg = row.segment_id ? segmentMap.get(row.segment_id) : null;
        return seg ? (
          <SegmentBadge name={seg.name} color={seg.color_hex} />
        ) : (
          <span className="text-slate-500">—</span>
        );
      },
    },
    {
      key: "clv_estimate",
      header: "CLV",
      render: (row) => formatCurrency(Number(row.clv_estimate)),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Customers"
        description="Browse and filter your customer base"
      />
      <FilterPanel
        search={search}
        onSearchChange={updateSearch}
        region={region}
        onRegionChange={(v) => {
          setRegion(v);
          setPage(1);
        }}
        valueTier={valueTier}
        onValueTierChange={(v) => {
          setValueTier(v);
          setPage(1);
        }}
        regions={[
          { label: "Andhra Pradesh", value: "Andhra Pradesh" },
          { label: "Arunachal Pradesh", value: "Arunachal Pradesh" },
          { label: "Assam", value: "Assam" },
          { label: "Bihar", value: "Bihar" },
          { label: "Chhattisgarh", value: "Chhattisgarh" },
          { label: "Goa", value: "Goa" },
          { label: "Gujarat", value: "Gujarat" },
          { label: "Haryana", value: "Haryana" },
          { label: "Himachal Pradesh", value: "Himachal Pradesh" },
          { label: "Jharkhand", value: "Jharkhand" },
          { label: "Karnataka", value: "Karnataka" },
          { label: "Kerala", value: "Kerala" },
          { label: "Madhya Pradesh", value: "Madhya Pradesh" },
          { label: "Maharashtra", value: "Maharashtra" },
          { label: "Manipur", value: "Manipur" },
          { label: "Meghalaya", value: "Meghalaya" },
          { label: "Mizoram", value: "Mizoram" },
          { label: "Nagaland", value: "Nagaland" },
          { label: "Odisha", value: "Odisha" },
          { label: "Punjab", value: "Punjab" },
          { label: "Rajasthan", value: "Rajasthan" },
          { label: "Sikkim", value: "Sikkim" },
          { label: "Tamil Nadu", value: "Tamil Nadu" },
          { label: "Telangana", value: "Telangana" },
          { label: "Tripura", value: "Tripura" },
          { label: "Uttar Pradesh", value: "Uttar Pradesh" },
          { label: "Uttarakhand", value: "Uttarakhand" },
          { label: "West Bengal", value: "West Bengal" },
          { label: "Delhi", value: "Delhi" },
          { label: "Other", value: "Other" },
        ]}
        valueTiers={[
          { label: "Premium", value: "premium" },
          { label: "Standard", value: "standard" },
        ]}
        onClear={() => {
          setSearch("");
          setSearchParams({}, { replace: true });
          setRegion("");
          setValueTier("");
          setPage(1);
        }}
        className="mb-4"
      />
      {isLoading ? (
        <TableSkeleton rows={8} />
      ) : (
        <DataTable
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(row) => row.id}
          page={data?.page ?? 1}
          pages={data?.pages ?? 1}
          onPageChange={setPage}
          onRowClick={(row) => setDrawerId(row.id)}
        />
      )}
      <CustomerDrawer
        customerId={drawerId}
        open={Boolean(drawerId)}
        onOpenChange={(open) => !open && setDrawerId(null)}
      />
      <p className="mt-4 text-center text-xs text-slate-600">
        Double-click a row or use drawer —{" "}
        <button
          type="button"
          className="text-cyan-400 hover:underline"
          onClick={() => drawerId && navigate(`/customers/${drawerId}`)}
        >
          open full detail
        </button>
      </p>
    </div>
  );
}