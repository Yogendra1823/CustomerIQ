import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { FileSpreadsheet, Upload } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { useUpload } from "@/hooks/useUpload";
import { cn } from "@/lib/utils";

export function UploadPage() {
  const { mutate, isPending, isSuccess, isError, data, progress } = useUpload();

  const onDrop = useCallback(
    (files: File[]) => {
      const file = files[0];
      if (file) mutate(file);
    },
    [mutate],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
    maxFiles: 1,
    disabled: isPending,
  });

  return (
    <div>
      <PageHeader
        title="Data upload"
        description="Import customer and transaction data from CSV or Excel"
      />
      <div
        {...getRootProps()}
        className={cn(
          "cursor-pointer rounded-2xl border-2 border-dashed p-16 text-center transition-colors",
          isDragActive
            ? "border-cyan-400 bg-cyan-500/10"
            : "border-slate-700 bg-slate-900/40 hover:border-slate-600",
          isPending && "pointer-events-none opacity-60",
        )}
      >
        <input {...getInputProps()} />
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-800 text-cyan-400">
          {isDragActive ? (
            <Upload className="h-8 w-8" />
          ) : (
            <FileSpreadsheet className="h-8 w-8" />
          )}
        </div>
        <p className="mt-4 text-lg font-medium text-slate-100">
          {isDragActive ? "Drop file here" : "Drag & drop your file"}
        </p>
        <p className="mt-2 text-sm text-slate-500">CSV, XLS, or XLSX up to 50MB</p>
        <Button className="mt-6" variant="secondary" type="button">
          Browse files
        </Button>
      </div>
      {isPending ? (
        <div className="mt-6">
          <div className="flex justify-between text-xs text-slate-500">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full bg-cyan-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      ) : null}
      {isSuccess && data?.data ? (
        <div className="mt-6 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
          {data.data.message} — {data.data.rows_imported} rows from {data.data.filename}
        </div>
      ) : null}
      {isError ? (
        <div className="mt-6 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          Upload failed. Ensure the API is running and the file format is valid.
        </div>
      ) : null}
    </div>
  );
}