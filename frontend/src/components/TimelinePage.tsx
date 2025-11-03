import {
  Shield,
  Upload,
  Search,
  Clock,
  Home,
  Settings,
  LogOut,
  Menu,
  FileText,
  Activity,
  Heart,
  Pill,
  Syringe,
  Stethoscope,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { ThemeToggle } from "./ThemeToggle";
import { StatusBadge } from "./StatusBadge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import { cacheService } from "../services/cache";
import { RecordDetailDialog } from "./RecordDetailDialog";

interface TimelinePageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function TimelinePage({ isDark, onToggleTheme, onNavigate }: TimelinePageProps) {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [records, setRecords] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);
  const [showRecordDialog, setShowRecordDialog] = useState(false);

  const handleLogout = async () => {
    await logout();
    onNavigate("landing");
  };

  const fetchTimeline = async (useCache = true) => {
    setIsLoading(true);
    setError("");

    try {
      // 1. Load from cache first
      if (useCache) {
        const cachedRecords = await cacheService.getCachedRecords();
        if (cachedRecords && cachedRecords.length > 0) {
          setRecords(cachedRecords);
          setIsLoading(false); // Show cached data immediately
        }
      }

      // 2. Fetch fresh data from API
      const response = await apiService.records.getAll({ limit: 100, offset: 0, order_by: 'created_at' });

      setRecords(response.records);
      await cacheService.cacheRecords(response.records);

    } catch (err: any) {
      console.error('Error fetching timeline:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load timeline');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getRecordIcon = (recordType: string) => {
    const type = recordType?.toLowerCase() || '';
    if (type.includes('lab') || type.includes('test')) return Activity;
    if (type.includes('consultation') || type.includes('visit')) return Stethoscope;
    if (type.includes('physical') || type.includes('checkup')) return Heart;
    if (type.includes('imaging') || type.includes('scan') || type.includes('x-ray') || type.includes('mri')) return FileText;
    if (type.includes('vaccination') || type.includes('vaccine')) return Syringe;
    if (type.includes('prescription') || type.includes('medication')) return Pill;
    return FileText;
  };

  const getRecordColor = (recordType: string) => {
    const type = recordType?.toLowerCase() || '';
    if (type.includes('lab') || type.includes('test')) return 'text-secondary';
    if (type.includes('consultation') || type.includes('visit')) return 'text-primary';
    if (type.includes('physical') || type.includes('checkup')) return 'text-success';
    if (type.includes('imaging')) return 'text-warning';
    if (type.includes('vaccination')) return 'text-purple-500';
    if (type.includes('prescription')) return 'text-pink-500';
    return 'text-primary';
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } bg-sidebar border-r border-border transition-all duration-300 overflow-hidden flex flex-col`}
      >
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-xl">MediVault</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("dashboard")}
          >
            <Home className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("upload")}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload Records
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => onNavigate("search")}
          >
            <Search className="mr-2 h-4 w-4" />
            Search Records
          </Button>
          <Button
            variant="secondary"
            className="w-full justify-start"
            onClick={() => onNavigate("timeline")}
          >
            <Clock className="mr-2 h-4 w-4" />
            Timeline
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </nav>

        <div className="p-4 border-t border-border space-y-2">
          <div className="flex items-center gap-3 p-2">
            <Avatar>
              <AvatarFallback className="bg-gradient-to-br from-primary to-secondary text-white">
                {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || ''}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-destructive hover:bg-destructive/10"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Bar */}
        <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-10">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Health Timeline</h1>
                <p className="text-sm text-muted-foreground">
                  Your complete medical history
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => fetchTimeline(false)}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
              </Button>
              <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
            </div>
          </div>
        </header>

        <div className="p-6 max-w-4xl mx-auto space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && records.length === 0 && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Loading your medical timeline...</p>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && records.length === 0 && !error && (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="flex justify-center mb-4">
                  <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                    <Clock className="h-8 w-8 text-muted-foreground" />
                  </div>
                </div>
                <h3 className="font-semibold mb-2">No Medical Records Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Your medical timeline is empty. Upload your first medical record to get started.
                </p>
                <Button onClick={() => onNavigate("upload")}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload First Record
                </Button>
              </CardContent>
            </Card>
          )}
          {/* Timeline */}
          {records.length > 0 && (
            <div className="relative">
              {/* Vertical Line */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border" />

              {/* Timeline Events */}
              <div className="space-y-8">
                {records.map((record) => {
                  const RecordIcon = getRecordIcon(record.record_type);
                  const colorClass = getRecordColor(record.record_type);

                  return (
                    <div key={record.id} className="relative pl-20">
                      {/* Timeline Dot */}
                      <div className="absolute left-0 flex items-start">
                        <div
                          className={`h-16 w-16 rounded-full bg-background border-2 border-border flex items-center justify-center ${colorClass}`}
                        >
                          <RecordIcon className="h-7 w-7" />
                        </div>
                      </div>

                      {/* Event Card */}
                      <Card className="hover:shadow-lg transition-shadow">
                        <CardContent className="p-6">
                          <div className="space-y-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="outline">{formatDate(record.created_at)}</Badge>
                                  {record.hospital && (
                                    <Badge variant="secondary">{record.hospital}</Badge>
                                  )}
                                </div>
                                <h3 className="font-semibold text-lg mb-1">
                                  {record.record_type || 'Medical Record'}
                                </h3>
                                {record.doctor_name && (
                                  <p className="text-sm text-muted-foreground mb-2">
                                    {record.doctor_name}
                                  </p>
                                )}
                                {record.clinical_summary && (
                                  <p className="text-sm line-clamp-3">{record.clinical_summary}</p>
                                )}
                              </div>
                            </div>

                            {record.extracted_text && (
                              <div className="bg-muted/50 rounded-lg p-4">
                                <p className="text-sm font-medium mb-2">Extracted Information:</p>
                                <p className="text-sm text-muted-foreground line-clamp-4">
                                  {record.extracted_text}
                                </p>
                              </div>
                            )}

                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setSelectedRecordId(record.id);
                                  setShowRecordDialog(true);
                                }}
                              >
                                <FileText className="mr-2 h-4 w-4" />
                                View Full Record
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={async () => {
                                  try {
                                    const blob = await apiService.records.download(record.id);
                                    const url = window.URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = record.filename || 'record.pdf';
                                    a.click();
                                    window.URL.revokeObjectURL(url);
                                  } catch (err) {
                                    console.error('Download failed:', err);
                                  }
                                }}
                              >
                                Download
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  );
                })}
              </div>

              {/* End of Timeline */}
              <div className="relative pl-20 mt-8">
                <div className="absolute left-0 flex items-start">
                  <div className="h-12 w-12 rounded-full bg-muted border-2 border-border flex items-center justify-center">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                  </div>
                </div>
                <p className="text-muted-foreground text-sm">
                  Beginning of your health records
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Record Detail Dialog */}
      <RecordDetailDialog
        recordId={selectedRecordId}
        open={showRecordDialog}
        onOpenChange={setShowRecordDialog}
      />
    </div>
  );
}
