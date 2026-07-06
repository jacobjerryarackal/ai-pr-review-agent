// For now, use mock data. We'll connect to the real API later.

interface Finding {
  id: string;
  repo: string;
  pr_number: number;
  title: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  message: string;
  file: string;
  line: number;
}

const mockFindings: Finding[] = [
  {
    id: "1",
    repo: "acme/api",
    pr_number: 42,
    title: "OAuth Login",
    severity: "HIGH",
    confidence: 0.62,
    message: "Missing input validation on OAuth callback URL",
    file: "auth.py",
    line: 42,
  },
  {
    id: "2",
    repo: "acme/api",
    pr_number: 43,
    title: "Database Migration",
    severity: "MEDIUM",
    confidence: 0.55,
    message: "Migration missing rollback script",
    file: "migrations/003.py",
    line: 15,
  },
];

export default function QueuePage() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        Approval Queue
      </h2>
      <p className="text-gray-600 mb-6">
        {mockFindings.length} findings need human review
      </p>

      <div className="space-y-4">
        {mockFindings.map((finding) => (
          <FindingCard key={finding.id} finding={finding} />
        ))}
      </div>
    </div>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  const confidenceColor =
    finding.confidence < 0.6
      ? "text-red-600 bg-red-50"
      : finding.confidence < 0.8
      ? "text-yellow-600 bg-yellow-50"
      : "text-green-600 bg-green-50";

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">
            {finding.repo} #{finding.pr_number} — {finding.title}
          </h3>
          <p className="text-sm text-gray-500">
            {finding.file}:{finding.line}
          </p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceColor}`}
        >
          {Math.round(finding.confidence * 100)}% confidence
        </span>
      </div>

      <div className="bg-gray-50 rounded p-4 mb-4">
        <p className="text-gray-700">
          <span className="font-semibold">{finding.severity}:</span>{" "}
          {finding.message}
        </p>
      </div>

      <div className="flex gap-3">
        <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          Approve
        </button>
        <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
          Reject
        </button>
        <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">
          View Diff
        </button>
      </div>
    </div>
  );
}