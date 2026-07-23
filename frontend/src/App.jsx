import { useState } from "react";
import { confirmSession, createGroups, uploadExcel } from "./api";
import CompassMark from "./components/CompassMark";
import GroupsView from "./components/GroupsView";
import PreviewModal from "./components/PreviewModal";
import ResultsView from "./components/ResultsView";
import Stepper from "./components/Stepper";
import UploadView from "./components/UploadView";

export default function App() {
  const [stage, setStage] = useState("upload");
  const [sessionId, setSessionId] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [results, setResults] = useState(null);
  const [groups, setGroups] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [creatingGroups, setCreatingGroups] = useState(false);

  const [uploadError, setUploadError] = useState(null);
  const [confirmError, setConfirmError] = useState(null);
  const [groupsError, setGroupsError] = useState(null);

  const unlocked = ["upload", results && "classification", groups && "groups"].filter(Boolean);

  async function handleFile(file) {
    setUploadError(null);
    setUploading(true);
    try {
      const data = await uploadExcel(file);
      setSessionId(data.session_id);
      setPreviewData(data);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleConfirm() {
    setConfirmError(null);
    setConfirming(true);
    try {
      const data = await confirmSession(sessionId);
      setResults(data.results);
      setPreviewData(null);
      setStage("classification");
    } catch (err) {
      setConfirmError(err.message);
    } finally {
      setConfirming(false);
    }
  }

  function handleCancelPreview() {
    setPreviewData(null);
    setSessionId(null);
    setConfirmError(null);
  }

  async function handleCreateGroups() {
    setGroupsError(null);
    setCreatingGroups(true);
    try {
      const data = await createGroups(sessionId);
      setGroups(data.groups);
      setStage("groups");
    } catch (err) {
      setGroupsError(err.message);
    } finally {
      setCreatingGroups(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <CompassMark />
          <div>
            <h1>FourSight</h1>
            <span className="brand-sub">Formación de equipos por perfil creativo</span>
          </div>
        </div>
        <Stepper stage={stage} unlocked={unlocked} onSelect={setStage} />
      </header>

      <main className="content">
        {stage === "upload" && (
          <UploadView onFile={handleFile} loading={uploading} error={uploadError} />
        )}

        {stage === "classification" && results && (
          <ResultsView
            results={results}
            onCreateGroups={handleCreateGroups}
            creatingGroups={creatingGroups}
            error={groupsError}
          />
        )}

        {stage === "groups" && groups && <GroupsView groups={groups} />}
      </main>

      {previewData && (
        <PreviewModal
          data={previewData}
          onConfirm={handleConfirm}
          onCancel={handleCancelPreview}
          confirming={confirming}
          error={confirmError}
        />
      )}
    </div>
  );
}
