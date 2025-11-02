import { Skeleton } from "./ui/skeleton";

interface RecordDetailDialogProps {
  recordId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function RecordDetailDialogSkeleton() {
  return (
    <DialogContent className="max-w-4xl max-h-[90vh]">
      <DialogHeader>
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </DialogHeader>
      <div className="space-y-6 pt-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-start gap-3">
            <Skeleton className="h-10 w-10 rounded-lg" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-32" />
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Skeleton className="h-10 w-10 rounded-lg" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-32" />
            </div>
          </div>
        </div>
        <Separator />
        <div>
          <Skeleton className="h-6 w-48 mb-4" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
        <Separator />
        <div>
          <Skeleton className="h-6 w-40 mb-4" />
          <div className="grid gap-3">
            <Skeleton className="h-12 w-full rounded-lg" />
            <Skeleton className="h-12 w-full rounded-lg" />
          </div>
        </div>
      </div>
    </DialogContent>
  );
}

export function RecordDetailDialog({
  recordId,
  open,
  onOpenChange,
}: RecordDetailDialogProps) {
  const [record, setRecord] = useState<any>(null);
  const [biomarkers, setBiomarkers] = useState<any[]>([]);
  const [medications, setMedications] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (recordId && open) {
      fetchRecordDetails();
    }
  }, [recordId, open]);

  const fetchRecordDetails = async () => {
    if (!recordId) return;

    setIsLoading(true);
    try {
      const response = await apiService.records.getById(recordId);
      setRecord(response.record);
      setBiomarkers(response.biomarkers || []);
      setMedications(response.medications || []);
      setAnomalies(response.anomalies || []);
    } catch (error) {
      console.error("Error fetching record details:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const handleDownload = async () => {
    if (!record?.id) return;

    try {
      const blob = await apiService.records.download(record.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = record.file_name || "medical-record.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  const getBiomarkerTrend = (biomarker: any) => {
    if (!biomarker.normal_min || !biomarker.normal_max) return null;
    if (biomarker.value < biomarker.normal_min) return "low";
    if (biomarker.value > biomarker.normal_max) return "high";
    return "normal";
  };

  const getBiomarkerIcon = (trend: string | null) => {
    if (trend === "high") return <TrendingUp className="h-4 w-4 text-red-500" />;
    if (trend === "low") return <TrendingDown className="h-4 w-4 text-yellow-500" />;
    return <Minus className="h-4 w-4 text-green-500" />;
  };

  if (isLoading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <RecordDetailDialogSkeleton />
      </Dialog>
    );
  }
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl">Medical Record Details</DialogTitle>
              <DialogDescription className="mt-2">
                {record?.file_name || "Untitled Record"}
              </DialogDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              className="ml-4"
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(90vh-8rem)] pr-4">
          <div className="space-y-6">
            {/* Record Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Calendar className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Document Date</p>
                  <p className="font-medium">
                    {formatDate(record?.document_date || record?.created_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Document Type</p>
                  <p className="font-medium capitalize">
                    {record?.document_type || "General Record"}
                  </p>
                </div>
              </div>

              {record?.issuing_hospital && (
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Hospital className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Hospital</p>
                    <p className="font-medium">{record.issuing_hospital}</p>
                  </div>
                </div>
              )}

              {record?.issuing_doctor && (
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Doctor</p>
                    <p className="font-medium">{record.issuing_doctor}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Clinical Summary */}
            {record?.clinical_summary && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Heart className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Clinical Summary</h3>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {record.clinical_summary}
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* Biomarkers */}
            {biomarkers.length > 0 && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Activity className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">
                      Biomarkers ({biomarkers.length})
                    </h3>
                  </div>
                  <div className="grid gap-3">
                    {biomarkers.map((biomarker, index) => {
                      const trend = getBiomarkerTrend(biomarker);
                      return (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 rounded-lg border bg-card"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            {getBiomarkerIcon(trend)}
                            <div>
                              <p className="font-medium capitalize">
                                {biomarker.biomarker_type.replace(/_/g, " ")}
                              </p>
                              {biomarker.measurement_date && (
                                <p className="text-xs text-muted-foreground">
                                  {formatDate(biomarker.measurement_date)}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold">
                              {biomarker.value} {biomarker.unit}
                            </p>
                            {biomarker.normal_min && biomarker.normal_max && (
                              <p className="text-xs text-muted-foreground">
                                Normal: {biomarker.normal_min}-{biomarker.normal_max}{" "}
                                {biomarker.unit}
                              </p>
                            )}
                          </div>
                          {biomarker.is_abnormal && (
                            <Badge variant="destructive" className="ml-2">
                              Abnormal
                            </Badge>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            )}

            {/* Medications */}
            {medications.length > 0 && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Pill className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">
                      Medications ({medications.length})
                    </h3>
                  </div>
                  <div className="grid gap-3">
                    {medications.map((med, index) => (
                      <div
                        key={index}
                        className="p-3 rounded-lg border bg-card space-y-2"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium">{med.medication_name}</p>
                            {med.dosage && (
                              <p className="text-sm text-muted-foreground">
                                Dosage: {med.dosage}
                              </p>
                            )}
                          </div>
                          {med.prescribed_date && (
                            <p className="text-xs text-muted-foreground">
                              {formatDate(med.prescribed_date)}
                            </p>
                          )}
                        </div>
                        {(med.frequency || med.duration) && (
                          <div className="flex gap-4 text-sm">
                            {med.frequency && (
                              <span className="text-muted-foreground">
                                Frequency: {med.frequency}
                              </span>
                            )}
                            {med.duration && (
                              <span className="text-muted-foreground">
                                Duration: {med.duration}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Anomalies */}
            {anomalies.length > 0 && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="h-5 w-5 text-orange-500" />
                    <h3 className="text-lg font-semibold">
                      Health Alerts ({anomalies.length})
                    </h3>
                  </div>
                  <div className="grid gap-3">
                    {anomalies.map((anomaly, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border ${
                          anomaly.is_critical
                            ? "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
                            : "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800"
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-semibold">{anomaly.title}</p>
                          <Badge
                            variant={anomaly.is_critical ? "destructive" : "secondary"}
                          >
                            Severity: {anomaly.severity}
                          </Badge>
                        </div>
                        <p className="text-sm mb-2">{anomaly.message}</p>
                        {anomaly.recommendation && (
                          <div className="mt-2 pt-2 border-t border-current/20">
                            <p className="text-sm font-medium mb-1">
                              Recommendation:
                            </p>
                            <p className="text-sm">{anomaly.recommendation}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* OCR Text */}
            {record?.ocr_text && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Extracted Text</h3>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 max-h-64 overflow-auto">
                    <pre className="text-sm whitespace-pre-wrap font-mono">
                      {record.ocr_text}
                    </pre>
                  </div>
                </div>
              </>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
