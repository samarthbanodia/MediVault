import {
  Shield,
  Upload,
  Search as SearchIcon,
  Clock,
  Home,
  Settings,
  LogOut,
  Menu,
  FileText,
  Calendar,
  Loader2,
  AlertCircle,
  Sparkles,
  Heart,
  Activity,
  Pill,
  AlertTriangle,
  TrendingUp,
  Filter,
  X,
  ChevronRight,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { ThemeToggle } from "./ThemeToggle";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { ScrollArea } from "./ui/scroll-area";
import { RecordDetailDialog } from "./RecordDetailDialog";
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";

interface SearchPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function SearchPage({ isDark, onToggleTheme, onNavigate }: SearchPageProps) {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [allRecords, setAllRecords] = useState<any[]>([]);
  const [displayedRecords, setDisplayedRecords] = useState<any[]>([]);
  const [aiSummary, setAiSummary] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingRecords, setIsLoadingRecords] = useState(true);
  const [error, setError] = useState("");
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);
  const [showRecordDialog, setShowRecordDialog] = useState(false);

  const handleLogout = async () => {
    await logout();
    onNavigate("landing");
  };

  // Load all records on mount
  useEffect(() => {
    fetchAllRecords();
  }, []);

  const fetchAllRecords = async () => {
    setIsLoadingRecords(true);
    setError("");

    try {
      const response = await apiService.records.getAll({
        limit: 100,
        offset: 0,
        order_by: 'created_at'
      });

      setAllRecords(response.records);
      setDisplayedRecords(response.records);
    } catch (err: any) {
      console.error('Error fetching records:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load records');
      setAllRecords([]);
      setDisplayedRecords([]);
    } finally {
      setIsLoadingRecords(false);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    // If search is empty, show all records
    if (!searchQuery.trim()) {
      setDisplayedRecords(allRecords);
      setAiSummary("");
      return;
    }

    setIsSearching(true);
    setError("");

    try {
      const result = await apiService.records.ask(searchQuery);

      setAiSummary(result.answer || "");
      setDisplayedRecords([]); // Clear records for now

    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.response?.data?.message || err.message || 'Search failed. Please try again.');
      // On error, show all records
      setDisplayedRecords(allRecords);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setDisplayedRecords(allRecords);
    setAiSummary("");
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'processing': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const handleRecordClick = (recordId: string) => {
    setSelectedRecordId(recordId);
    setShowRecordDialog(true);
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
            <span className="font-bold text-xl">MediSense</span>
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
            variant="secondary"
            className="w-full justify-start"
            onClick={() => onNavigate("search")}
          >
            <SearchIcon className="mr-2 h-4 w-4" />
            Search Records
          </Button>
          <Button
            variant="ghost"
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
                <h1 className="text-2xl font-bold">Smart Search</h1>
                <p className="text-sm text-muted-foreground">
                  Search through your medical records with AI
                </p>
              </div>
            </div>
            <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
          </div>
        </header>

        <div className="p-6 max-w-7xl mx-auto space-y-6">
          {/* Search Bar */}
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={handleSearch} className="flex gap-3">
                <div className="relative flex-1">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search your medical records... (e.g., 'blood pressure', 'diabetes', 'medications')"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-10 h-12 text-base"
                  />
                  {searchQuery && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={clearSearch}
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <Button
                  type="submit"
                  size="lg"
                  disabled={isSearching}
                  className="px-8"
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5" />
                      AI Search
                    </>
                  )}
                </Button>
              </form>

              {searchQuery && (
                <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                  <Sparkles className="h-4 w-4" />
                  <span>AI-powered semantic search active</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Summary */}
          {aiSummary && (
            <Card className="border-primary/50 bg-gradient-to-r from-primary/5 to-secondary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  AI Interpretation
                </CardTitle>
                <CardDescription>
                  Here's what I found in your medical records
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-base leading-relaxed whitespace-pre-wrap">
                  {aiSummary}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Error Message */}
          {error && (
            <Card className="border-destructive bg-destructive/5">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-destructive">Error</p>
                    <p className="text-sm text-muted-foreground mt-1">{error}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Records Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">
                {searchQuery ? `Search Results (${displayedRecords.length})` : `All Records (${displayedRecords.length})`}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                {searchQuery
                  ? "Click any record to view AI interpretation and details"
                  : "Browse all your medical records or search above"}
              </p>
            </div>
            {displayedRecords.length > 0 && (
              <Button variant="outline" size="sm" onClick={fetchAllRecords}>
                <Activity className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            )}
          </div>

          {/* Loading State */}
          {isLoadingRecords && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Loading your medical records...</p>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!isLoadingRecords && displayedRecords.length === 0 && !error && (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">
                    {searchQuery ? "No matching records found" : "No medical records yet"}
                  </h3>
                  <p className="text-muted-foreground mb-6">
                    {searchQuery
                      ? "Try a different search term or clear the search to see all records"
                      : "Upload your first medical document to get started"}
                  </p>
                  {searchQuery ? (
                    <Button onClick={clearSearch} variant="outline">
                      Clear Search
                    </Button>
                  ) : (
                    <Button onClick={() => onNavigate("upload")}>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload First Record
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Records Grid */}
          {!isLoadingRecords && displayedRecords.length > 0 && (
            <div className="grid gap-4">
              {displayedRecords.map((record) => (
                <Card
                  key={record.id}
                  className="hover:border-primary/50 transition-all cursor-pointer group"
                  onClick={() => handleRecordClick(record.id)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 space-y-3">
                        {/* Header */}
                        <div className="flex items-start gap-4">
                          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <FileText className="h-6 w-6 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">
                              {record.file_name || "Untitled Record"}
                            </h3>
                            <div className="flex items-center gap-3 mt-1 flex-wrap">
                              <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                <span>{formatDate(record.document_date || record.created_at)}</span>
                              </div>
                              {record.document_type && (
                                <Badge variant="secondary" className="capitalize">
                                  {record.document_type.replace(/_/g, ' ')}
                                </Badge>
                              )}
                              <Badge className={getStatusColor(record.processing_status)}>
                                {record.processing_status}
                              </Badge>
                            </div>
                          </div>
                        </div>

                        {/* Clinical Summary Preview */}
                        {record.clinical_summary && (
                          <div className="bg-muted/50 rounded-lg p-3">
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {record.clinical_summary}
                            </p>
                          </div>
                        )}

                        {/* Quick Stats */}
                        <div className="flex items-center gap-4 pt-2">
                          {record.has_critical_alerts && (
                            <div className="flex items-center gap-1.5 text-sm text-destructive">
                              <AlertTriangle className="h-4 w-4" />
                              <span className="font-medium">Critical Alert</span>
                            </div>
                          )}
                          {record.overall_severity > 0 && (
                            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                              <Activity className="h-4 w-4" />
                              <span>Severity: {record.overall_severity}/100</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Action Button */}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="ml-4 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRecordClick(record.id);
                        }}
                      >
                        <span className="mr-2">View Details</span>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
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
