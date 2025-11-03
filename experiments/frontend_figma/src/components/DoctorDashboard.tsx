import {
  Shield,
  Search,
  Settings,
  LogOut,
  Menu,
  User,
  Activity,
  Calendar,
  FileText,
  Plus,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { ThemeToggle } from "./ThemeToggle";
import { StatusBadge } from "./StatusBadge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";

interface DoctorDashboardProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

export function DoctorDashboard({ isDark, onToggleTheme, onNavigate }: DoctorDashboardProps) {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [patientDetails, setPatientDetails] = useState<any>(null);
  const [recentRecords, setRecentRecords] = useState<any[]>([]);
  const [clinicalNotes, setNotes] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [noteText, setNoteText] = useState("");
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    onNavigate("landing");
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!searchQuery.trim()) {
      setError("Please enter a patient email or ID");
      return;
    }

    setIsSearching(true);
    setError("");

    try {
      const result = await apiService.doctor.searchPatients(searchQuery);
      setSearchResults(result.patients);

      if (result.patients.length === 1) {
        // Auto-select if only one result
        await loadPatientDetails(result.patients[0].id);
      }
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.response?.data?.message || err.message || 'Search failed');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const loadPatientDetails = async (patientId: string) => {
    setIsLoading(true);
    setError("");

    try {
      const [details, notes, anomaliesResult] = await Promise.all([
        apiService.doctor.getPatientDetails(patientId),
        apiService.doctor.getPatientNotes(patientId),
        apiService.doctor.getPatientAnomalies(patientId, { unacknowledged_only: true })
      ]);

      setSelectedPatient(details.patient);
      setPatientDetails(details);
      setRecentRecords(details.recent_records || []);
      setNotes(notes.notes || []);
      setAnomalies(anomaliesResult.anomalies || []);
    } catch (err: any) {
      console.error('Error loading patient:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load patient details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim() || !selectedPatient) {
      setError("Please enter a note");
      return;
    }

    setIsAddingNote(true);
    setError("");

    try {
      await apiService.doctor.addPatientNote(selectedPatient.id, {
        note_text: noteText,
        note_type: 'observation'
      });

      // Reload notes
      const notesResult = await apiService.doctor.getPatientNotes(selectedPatient.id);
      setNotes(notesResult.notes || []);

      setNoteText("");
      setIsDialogOpen(false);
    } catch (err: any) {
      console.error('Error adding note:', err);
      setError(err.response?.data?.message || err.message || 'Failed to add note');
    } finally {
      setIsAddingNote(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const calculateAge = (dob: string) => {
    if (!dob) return null;
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
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
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-secondary to-primary flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="font-bold text-xl block">MediVault</span>
              <span className="text-xs text-muted-foreground">Provider Portal</span>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant="secondary"
            className="w-full justify-start"
            onClick={() => onNavigate("doctor-dashboard")}
          >
            <User className="mr-2 h-4 w-4" />
            Patient Search
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Calendar className="mr-2 h-4 w-4" />
            Appointments
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <FileText className="mr-2 h-4 w-4" />
            My Patients
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </nav>

        <div className="p-4 border-t border-border space-y-2">
          <div className="flex items-center gap-3 p-2">
            <Avatar>
              <AvatarFallback className="bg-gradient-to-br from-secondary to-primary text-white">
                {user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'D'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{user?.full_name || 'Doctor'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.specialty || user?.email || ''}</p>
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
                <h1 className="text-2xl font-bold">Patient Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  View and manage patient records
                </p>
              </div>
            </div>
            <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
          </div>
        </header>

        <div className="p-6 max-w-7xl mx-auto space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Patient Search */}
          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSearch}>
                <div className="space-y-2">
                  <Label htmlFor="patientSearch">Search Patient</Label>
                  <div className="flex gap-4">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                      <Input
                        id="patientSearch"
                        placeholder="Enter patient email or ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                        disabled={isSearching}
                      />
                    </div>
                    <Button
                      type="submit"
                      disabled={isSearching || !searchQuery.trim()}
                    >
                      {isSearching ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Searching...
                        </>
                      ) : (
                        <>
                          <Search className="mr-2 h-4 w-4" />
                          Search
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </form>

              {/* Search Results */}
              {searchResults.length > 1 && (
                <div className="mt-4 pt-4 border-t space-y-2">
                  <p className="text-sm font-medium">Search Results ({searchResults.length})</p>
                  <div className="space-y-2">
                    {searchResults.map((patient) => (
                      <div
                        key={patient.id}
                        className="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer flex items-center justify-between"
                        onClick={() => loadPatientDetails(patient.id)}
                      >
                        <div>
                          <p className="font-medium">{patient.full_name}</p>
                          <p className="text-sm text-muted-foreground">{patient.email}</p>
                        </div>
                        <Button variant="outline" size="sm">View</Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Loading patient details...</p>
              </div>
            </div>
          )}

          {/* Patient Info Card (shown when patient is selected) */}
          {selectedPatient && !isLoading && (
            <>
              <Card className="border-2 border-secondary/20">
                <CardHeader className="bg-secondary/5">
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5 text-secondary" />
                    Patient Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Name</p>
                        <p className="font-semibold text-lg">{selectedPatient.full_name}</p>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        {selectedPatient.date_of_birth && (
                          <div>
                            <p className="text-sm text-muted-foreground">Age</p>
                            <p className="font-semibold">{calculateAge(selectedPatient.date_of_birth)}</p>
                          </div>
                        )}
                        {selectedPatient.gender && (
                          <div>
                            <p className="text-sm text-muted-foreground">Gender</p>
                            <p className="font-semibold">{selectedPatient.gender}</p>
                          </div>
                        )}
                        {selectedPatient.blood_type && (
                          <div>
                            <p className="text-sm text-muted-foreground">Blood Type</p>
                            <p className="font-semibold">{selectedPatient.blood_type}</p>
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Email</p>
                        <p className="text-sm">{selectedPatient.email}</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {selectedPatient.phone && (
                        <div>
                          <p className="text-sm text-muted-foreground">Phone</p>
                          <p className="font-semibold">{selectedPatient.phone}</p>
                        </div>
                      )}
                      {anomalies.length > 0 && (
                        <div>
                          <p className="text-sm text-muted-foreground mb-2">Critical Alerts</p>
                          <div className="flex flex-wrap gap-2">
                            {anomalies.slice(0, 3).map((anomaly) => (
                              <Badge key={anomaly.id} variant="destructive">
                                {anomaly.biomarker_type}: {anomaly.severity}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-muted-foreground">Total Records</p>
                        <p className="font-semibold">{recentRecords.length}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Anomalies & Alerts */}
              {anomalies.length > 0 && (
                <Card className="border-destructive/20">
                  <CardHeader className="bg-destructive/5">
                    <CardTitle className="flex items-center gap-2 text-destructive">
                      <AlertCircle className="h-5 w-5" />
                      Critical Anomalies ({anomalies.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="space-y-3">
                      {anomalies.map((anomaly) => (
                        <div
                          key={anomaly.id}
                          className="p-4 border border-destructive/20 rounded-lg"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="font-medium">{anomaly.biomarker_type}</p>
                                <Badge variant="destructive">{anomaly.severity}</Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                Value: {anomaly.biomarker_value} | Threshold: {anomaly.threshold_value}
                              </p>
                              <p className="text-sm mt-1">{anomaly.description}</p>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Detected: {formatDate(anomaly.detected_at)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recent Records & Clinical Notes */}
              <div className="grid md:grid-cols-2 gap-6">
                {/* Recent Records */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Recent Records ({recentRecords.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    {recentRecords.length > 0 ? (
                      <div className="space-y-3">
                        {recentRecords.slice(0, 5).map((record) => (
                          <div
                            key={record.id}
                            className="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <p className="font-medium text-sm">{record.record_type || 'Medical Record'}</p>
                                <p className="text-xs text-muted-foreground">
                                  {formatDate(record.created_at)}
                                  {record.hospital && ` • ${record.hospital}`}
                                </p>
                                {record.clinical_summary && (
                                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                    {record.clinical_summary}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No records found
                      </p>
                    )}
                  </CardContent>
                </Card>

                {/* Clinical Notes */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Clinical Notes ({clinicalNotes.length})
                      </CardTitle>
                      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                          <Button size="sm">
                            <Plus className="mr-1 h-4 w-4" />
                            Add Note
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Add Clinical Note</DialogTitle>
                            <DialogDescription>
                              Add observations or notes for {selectedPatient.full_name}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="space-y-2">
                              <Label htmlFor="note">Clinical Note</Label>
                              <Textarea
                                id="note"
                                placeholder="Enter your clinical observations..."
                                rows={6}
                                value={noteText}
                                onChange={(e) => setNoteText(e.target.value)}
                                disabled={isAddingNote}
                              />
                            </div>
                            <Button
                              onClick={handleAddNote}
                              className="w-full"
                              disabled={isAddingNote || !noteText.trim()}
                            >
                              {isAddingNote ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Saving...
                                </>
                              ) : (
                                'Save Note'
                              )}
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    {clinicalNotes.length > 0 ? (
                      <div className="space-y-4">
                        {clinicalNotes.map((note) => (
                          <div key={note.id} className="pb-4 border-b last:border-0">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <p className="font-medium text-sm">{note.doctor_name || user?.full_name || 'Doctor'}</p>
                                <p className="text-xs text-muted-foreground">{formatDate(note.created_at)}</p>
                              </div>
                              {note.note_type && (
                                <Badge variant="outline">{note.note_type}</Badge>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground">{note.note_text}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No clinical notes yet. Add the first note above.
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
