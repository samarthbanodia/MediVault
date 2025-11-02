import {
  Shield,
  Upload as UploadIcon,
  FileText,
  X,
  CheckCircle2,
  Home,
  Search,
  Clock,
  Settings,
  LogOut,
  Menu,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { ThemeToggle } from "./ThemeToggle";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Progress } from "./ui/progress";
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiService } from "../services/api";
import { cacheService } from "../services/cache";

interface UploadPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onNavigate: (page: string) => void;
}

interface UploadedFile {
  file: File;  // Store the actual File object
  name: string;
  size: number;
  type: string;
  status?: 'pending' | 'uploading' | 'success' | 'error';
  progress?: number;
  error?: string;
}

export function UploadPage({ isDark, onToggleTheme, onNavigate }: UploadPageProps) {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [formData, setFormData] = useState({
    hospital: "",
    doctor: "",
    visitDate: "",
    notes: "",
  });

  const handleLogout = async () => {
    await logout();
    onNavigate("landing");
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    // Filter out files that are too large (>10MB) or unsupported types
    const validFiles = newFiles.filter((file) => {
      const maxSize = 10 * 1024 * 1024; // 10MB
      const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

      if (file.size > maxSize) {
        setError(`File "${file.name}" is too large. Maximum size is 10MB.`);
        return false;
      }

      if (!validTypes.includes(file.type)) {
        setError(`File "${file.name}" has an unsupported format. Please use PDF, JPG, or PNG.`);
        return false;
      }

      return true;
    });

    const uploadedFiles: UploadedFile[] = validFiles.map((file) => ({
      file,  // Store the actual File object
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
    }));

    setFiles([...files, ...uploadedFiles]);
    setError(""); // Clear any previous errors
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleUpload = async () => {
    setIsUploading(true);
    setError("");
    setSuccessMessage("");

    try {
      let successCount = 0;
      let failCount = 0;

      // Upload each file sequentially
      for (let i = 0; i < files.length; i++) {
        const fileData = files[i];

        // Update file status to uploading
        setFiles(prev => prev.map((f, idx) =>
          idx === i ? { ...f, status: 'uploading' as const, progress: 0 } : f
        ));

        try {
          // Prepare metadata
          const metadata: any = {};
          if (formData.hospital) metadata.hospital = formData.hospital;
          if (formData.doctor) metadata.doctor_name = formData.doctor;
          if (formData.visitDate) metadata.visit_date = formData.visitDate;
          if (formData.notes) metadata.notes = formData.notes;

          // Upload the file
          const result = await apiService.records.upload(fileData.file, metadata);

          // Update file status to success
          setFiles(prev => prev.map((f, idx) =>
            idx === i ? { ...f, status: 'success' as const, progress: 100 } : f
          ));

          successCount++;

          // Invalidate cached records so they get refreshed
          await cacheService.clearUserData('dashboard_summary');
          await cacheService.clearRecords();
          await cacheService.clearAnomalies();

        } catch (err: any) {
          console.error(`Error uploading ${fileData.name}:`, err);

          // Update file status to error
          setFiles(prev => prev.map((f, idx) =>
            idx === i ? {
              ...f,
              status: 'error' as const,
              error: err.response?.data?.message || err.message || 'Upload failed'
            } : f
          ));

          failCount++;
        }
      }

      // Show summary message
      if (successCount > 0 && failCount === 0) {
        setSuccessMessage(`Successfully uploaded ${successCount} ${successCount === 1 ? 'file' : 'files'}!`);

        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          onNavigate("dashboard");
        }, 2000);
      } else if (successCount > 0 && failCount > 0) {
        setSuccessMessage(`Uploaded ${successCount} ${successCount === 1 ? 'file' : 'files'}. ${failCount} failed.`);
      } else {
        setError(`Failed to upload ${failCount} ${failCount === 1 ? 'file' : 'files'}. Please try again.`);
      }

    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'An unexpected error occurred during upload');
    } finally {
      setIsUploading(false);
    }
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
            variant="secondary"
            className="w-full justify-start"
            onClick={() => onNavigate("upload")}
          >
            <UploadIcon className="mr-2 h-4 w-4" />
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
                <h1 className="text-2xl font-bold">Upload Records</h1>
                <p className="text-sm text-muted-foreground">
                  Add new medical documents to your vault
                </p>
              </div>
            </div>
            <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
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

          {/* Success Message */}
          {successMessage && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800 dark:text-green-200">{successMessage}</p>
            </div>
          )}

          {/* Drag & Drop Zone */}
          <Card>
            <CardContent className="p-0">
              <div
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  isDragging
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-primary/50"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                      <UploadIcon className="h-8 w-8 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">
                      Drag and drop files here
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      or click to browse
                    </p>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload">
                      <Button asChild>
                        <span>Select Files</span>
                      </Button>
                    </label>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Supported formats: PDF, JPG, PNG (Max 10MB per file)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* File List */}
          {files.length > 0 && (
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-semibold">Selected Files ({files.length})</h3>
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="p-3 bg-muted rounded-lg space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <FileText className="h-5 w-5 text-primary shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{file.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {/* Status Indicator */}
                          {file.status === 'uploading' && (
                            <Loader2 className="h-4 w-4 text-primary animate-spin" />
                          )}
                          {file.status === 'success' && (
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          )}
                          {file.status === 'error' && (
                            <AlertCircle className="h-4 w-4 text-red-600" />
                          )}
                          {file.status === 'pending' && !isUploading && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => removeFile(index)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      {/* Error message */}
                      {file.error && (
                        <p className="text-xs text-red-600 dark:text-red-400">
                          {file.error}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Metadata Form */}
          {files.length > 0 && (
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-semibold">Record Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="hospital">Hospital/Clinic</Label>
                    <Input
                      id="hospital"
                      placeholder="City General Hospital"
                      value={formData.hospital}
                      onChange={(e) =>
                        setFormData({ ...formData, hospital: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="doctor">Doctor Name</Label>
                    <Input
                      id="doctor"
                      placeholder="Dr. Sarah Johnson"
                      value={formData.doctor}
                      onChange={(e) =>
                        setFormData({ ...formData, doctor: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="visitDate">Visit Date</Label>
                  <Input
                    id="visitDate"
                    type="date"
                    value={formData.visitDate}
                    onChange={(e) =>
                      setFormData({ ...formData, visitDate: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notes">Additional Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Add any relevant notes about this visit..."
                    rows={4}
                    value={formData.notes}
                    onChange={(e) =>
                      setFormData({ ...formData, notes: e.target.value })
                    }
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload Button */}
          {files.length > 0 && (
            <div className="flex gap-4">
              <Button
                className="flex-1"
                size="lg"
                onClick={handleUpload}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="mr-2 h-5 w-5" />
                    Upload {files.length} {files.length === 1 ? "File" : "Files"}
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  setFiles([]);
                  setError("");
                  setSuccessMessage("");
                }}
                disabled={isUploading}
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
