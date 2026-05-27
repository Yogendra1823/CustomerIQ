import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { uploadApi } from "@/lib/api";

export function useUpload() {
  const [progress, setProgress] = useState(0);

  const mutation = useMutation({
    mutationFn: (file: File) =>
      uploadApi.upload(file, (pct) => setProgress(pct)),
    onMutate: () => setProgress(0),
  });

  return { ...mutation, progress };
}