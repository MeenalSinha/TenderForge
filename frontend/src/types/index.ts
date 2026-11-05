export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'Viewer' | 'Author' | 'Reviewer' | 'Approver' | 'Admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  invited_by?: string;
  created_at: string;
}

export interface Tender {
  id: string;
  workspace_id: string;
  title: string;
  reference_number?: string;
  issuing_authority?: string;
  procurement_category?: string;
  estimated_value?: number;
  currency: string;
  status: string;
  submission_deadline?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  original_filename: string;
  document_category: string;
  file_size_bytes: number;
  checksum_sha256: string;
  processing_status: string;
  created_at: string;
}

export interface Requirement {
  id: string;
  tender_id: string;
  category: 'eligibility' | 'technical' | 'financial' | 'submission' | 'general';
  classification: 'mandatory' | 'optional' | 'desirable';
  description: string;
  source_page?: number;
  source_offset?: number;
  source_excerpt?: string;
  confidence_score: number;
}

export interface BidEvaluation {
  id: string;
  tender_id: string;
  overall_score: number;
  eligibility_gates_passed: boolean;
  recommendation: 'BID' | 'BID WITH CONDITIONS' | 'NO-BID RECOMMENDED';
  dimensions: Record<string, any>;
  human_decision: 'PENDING' | 'APPROVED_BID' | 'APPROVED_NO_BID' | 'OVERRIDDEN';
  human_decision_by?: string;
  human_decision_rationale?: string;
}

export interface ComplianceItem {
  id: string;
  requirement_id: string;
  requirement_text: string;
  compliance_status: 'Compliant' | 'Clarification Needed' | 'Non-Compliant';
  risk_level: 'Low' | 'Medium' | 'High';
  evidence_claim?: string;
  clarification_notes?: string;
}

export interface EvidenceItem {
  id: string;
  organization_id: string;
  title: string;
  evidence_type: string;
  freshness_status: 'Fresh' | 'Expiring_Soon' | 'Expired';
  valid_until?: string;
}

export interface Contradiction {
  id: string;
  claim_field: string;
  value_1: string;
  value_2: string;
  contradiction_severity: string;
  status: 'Open' | 'Investigating' | 'Resolved' | 'Dismissed';
  resolution_notes?: string;
}

export interface BOQItem {
  id?: string;
  item_code: string;
  description: string;
  category: string;
  quantity: number;
  unit: string;
  unit_cost: number;
  tax_rate: number;
  total_price: number;
}
