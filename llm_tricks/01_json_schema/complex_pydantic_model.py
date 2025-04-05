#!/usr/bin/env python3
"""
Extremely complex Pydantic model example to demonstrate the importance of schema formatting.

This file contains a deeply nested, complex enterprise-grade data model with:
- Multiple levels of inheritance
- Circular references
- Nested arrays and objects
- Various field types and validators
- Complex validation rules

When converted to a JSON schema, this will be extremely difficult for LLMs to parse
unless properly formatted.
"""

import enum
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator

# --- Enums and Constants ---


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"


class TaskStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResourceType(str, enum.Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class ComplianceLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentSeverity(int, enum.Enum):
    TRIVIAL = 1
    MINOR = 2
    MAJOR = 3
    CRITICAL = 4
    BLOCKER = 5


# Define custom validators for types
def positive_decimal(v: Decimal) -> Decimal:
    if v < 0:
        raise ValueError("must be greater than or equal to 0")
    return v


def validate_ge1_le1000(v: int) -> int:
    if v < 1 or v > 1000:
        raise ValueError("must be between 1 and 1000")
    return v


def validate_ge1_le5(v: int) -> int:
    if v < 1 or v > 5:
        raise ValueError("must be between 1 and 5")
    return v


def validate_ge0_le100(v: int) -> int:
    if v < 0 or v > 100:
        raise ValueError("must be between 0 and 100")
    return v


def validate_ge1_le100(v: int) -> int:
    if v < 1 or v > 100:
        raise ValueError("must be between 1 and 100")
    return v


# Custom types
PositiveDecimal = Annotated[Decimal, AfterValidator(positive_decimal)]
IntGE1LE1000 = Annotated[int, AfterValidator(validate_ge1_le1000)]
IntGE1LE5 = Annotated[int, AfterValidator(validate_ge0_le100)]
IntGE0LE100 = Annotated[int, AfterValidator(validate_ge0_le100)]
IntGE1LE100 = Annotated[int, AfterValidator(validate_ge1_le100)]

# --- Base Models ---


class AuditInfo(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime | None = None
    modified_by: str | None = None
    version: int = Field(default=1, ge=1)

    @field_validator("modified_at")
    @classmethod
    def modified_at_must_be_after_created_at(cls, v: datetime | None, info):
        if v and "created_at" in info.data and v < info.data["created_at"]:
            raise ValueError("modified_at must be after created_at")
        return v


class GeoLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float | None = None
    accuracy: float | None = Field(None, ge=0)
    timestamp: datetime | None = None


class Address(BaseModel):
    street_1: str = Field(..., min_length=1, max_length=100)
    street_2: str | None = Field(None, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(..., min_length=2, max_length=2)
    location: GeoLocation | None = None


class Contact(BaseModel):
    email: EmailStr
    phone: str | None = Field(None, min_length=8, max_length=15)
    alternative_email: EmailStr | None = None
    emergency_contact: str | None = None
    social_profiles: dict[str, HttpUrl] = Field(default_factory=dict)
    preferred_contact_method: Literal["email", "phone", "sms"] = "email"


class TaggedItem(BaseModel):
    tags: set[str] = Field(default_factory=set)
    labels: dict[str, str] = Field(default_factory=dict)
    categories: list[str] = Field(default_factory=list)

    class Config:
        extra = "allow"


class MonetaryAmount(BaseModel):
    amount: PositiveDecimal = Field(...)
    currency: str = Field(..., min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def currency_must_be_uppercase(cls, v: str) -> str:
        return v.upper()


# --- Network Models ---


class NetworkInterface(BaseModel):
    name: str
    mac_address: str | None = None
    ipv4: IPv4Address | None = None
    ipv6: IPv6Address | None = None
    subnet_mask: str | None = None
    gateway: str | None = None
    dns_servers: list[str] = Field(default_factory=list)
    is_dhcp_enabled: bool = True
    is_primary: bool = False
    speed_mbps: int | None = None
    status: Literal["up", "down", "unknown"] = "unknown"


class FirewallRule(BaseModel):
    # id: str = Field(default_factory=uuid.str)
    name: str = Field(..., min_length=3, max_length=50)
    description: str | None = None
    source_ip: IPv4Address | IPv6Address | str
    destination_ip: IPv4Address | IPv6Address | str
    protocol: Literal["tcp", "udp", "icmp", "any"]
    source_port: int | str | None = None
    destination_port: int | str | None = None
    action: Literal["allow", "deny", "log"]
    direction: Literal["inbound", "outbound"]
    priority: IntGE1LE1000 = 500
    enabled: bool = True


class NetworkConfig(BaseModel):
    hostname: str
    domain: str | None = None
    interfaces: list[NetworkInterface] = Field(default_factory=list)
    firewall_rules: list[FirewallRule] = Field(default_factory=list)
    vpn_enabled: bool = False
    proxy_settings: dict[str, Any] | None = None

    @field_validator("hostname")
    @classmethod
    def hostname_must_be_valid(cls, v: str) -> str:
        if len(v) > 63 or not all(c.isalnum() or c == '-' for c in v):
            raise ValueError("Invalid hostname")
        return v


# --- Security Models ---


class Permission(BaseModel):
    resource: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    conditions: dict[str, Any] | None = None


class AuthenticationMethod(BaseModel):
    last_used: datetime | None = None
    enabled: bool = True
    additional_settings: dict[str, Any] = Field(default_factory=dict)


class SecurityClearance(BaseModel):
    level: int = Field(..., ge=0, le=10)
    granted_by: str
    granted_at: datetime
    expires_at: datetime | None = None
    revocable: bool = True

    @field_validator("expires_at")
    @classmethod
    def expires_at_must_be_future(cls, v: datetime | None, info):
        if v and "granted_at" in info.data and v < info.data["granted_at"]:
            raise ValueError("expires_at must be after granted_at")
        return v


class UserSecurity(BaseModel):
    permissions: list[Permission] = Field(default_factory=list)
    roles: list[UserRole] = Field(default_factory=list)
    authentication_methods: list[AuthenticationMethod] = Field(default_factory=list)
    failed_login_attempts: int = 0
    account_locked: bool = False
    last_password_change: datetime | None = None
    password_expiry: datetime | None = None
    security_questions: dict[str, str] = Field(default_factory=dict)
    clearance: SecurityClearance | None = None


# --- Resource Models ---


class ResourceMetrics(BaseModel):
    cpu_usage_percent: float = Field(..., ge=0, le=100)
    memory_usage_bytes: int = Field(..., ge=0)
    disk_read_bytes: int = Field(..., ge=0)
    disk_write_bytes: int = Field(..., ge=0)
    network_in_bytes: int = Field(..., ge=0)
    network_out_bytes: int = Field(..., ge=0)
    iops: int = Field(..., ge=0)
    latency_ms: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)


class ResourceQuota(BaseModel):
    cpu_cores: float | None = None
    memory_gb: float | None = None
    storage_gb: float | None = None
    network_bandwidth_mbps: int | None = None
    iops: int | None = None


class ResourceLimits(BaseModel):
    quota: ResourceQuota
    throttling_enabled: bool = False
    throttling_threshold_percent: int | None = Field(None, ge=1, le=100)
    auto_scale_enabled: bool = False
    min_instances: int | None = Field(None, ge=0)
    max_instances: int | None = Field(None, ge=1)


class ResourceCost(BaseModel):
    hourly_rate: MonetaryAmount
    monthly_estimated: MonetaryAmount
    last_billed_amount: MonetaryAmount | None = None
    billing_cycle_start: date | None = None
    billing_cycle_end: date | None = None
    cost_center: str | None = None
    budget_code: str | None = None


class Resource(TaggedItem, AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    name: str = Field(..., min_length=3, max_length=50)
    description: str | None = None
    type: ResourceType
    status: Literal["provisioning", "running", "paused", "stopped", "terminated"] = "provisioning"
    owner: str
    network_config: NetworkConfig | None = None
    metrics: ResourceMetrics | None = None
    limits: ResourceLimits | None = None
    cost: ResourceCost | None = None
    location: str | None = None
    availability_zone: str | None = None
    is_highly_available: bool = False
    compliance_level: ComplianceLevel = ComplianceLevel.LOW

    @model_validator(mode='after')
    def check_high_availability_requirements(self):
        if self.is_highly_available and self.compliance_level != ComplianceLevel.HIGH:
            raise ValueError("Highly available resources must have critical compliance level")
        return self


# --- User Models ---


class UserProfile(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    avatar_url: HttpUrl | None = None
    title: str | None = None
    department: str | None = None
    bio: str | None = Field(None, max_length=500)
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    timezone: str | None = None
    theme_preference: Literal["light", "dark", "system"] = "system"
    notification_preferences: dict[str, bool] = Field(default_factory=dict)


class WorkSchedule(BaseModel):
    days_of_week: list[int] = Field(default_factory=list)  # 0 = Monday, 6 = Sunday
    start_time: time
    end_time: time
    lunch_break_minutes: int = 60
    flexible_hours: bool = False
    time_zone: str = "UTC"

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: list[int]) -> list[int]:
        if not all(0 <= day <= 6 for day in v):
            raise ValueError("Days must be between 0 (Monday) and 6 (Sunday)")
        return v

    @field_validator("end_time")
    @classmethod
    def end_time_after_start_time(cls, v: time, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class EmploymentDetails(BaseModel):
    employee_id: str
    hire_date: date
    job_title: str
    department: str
    manager: str | None = None
    employment_type: Literal["full_time", "part_time", "contract", "intern"]
    salary_band: str | None = None
    work_schedule: WorkSchedule | None = None
    is_remote: bool = False
    office_location: str | None = None
    probation_end_date: date | None = None


class User(TaggedItem, AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True
    is_verified: bool = False
    primary_role: UserRole = UserRole.VIEWER
    secondary_roles: list[UserRole] = Field(default_factory=list)
    date_of_birth: date | None = None
    profile: UserProfile
    contact: Contact
    address: Address | None = None
    security: UserSecurity
    employment: EmploymentDetails | None = None
    managed_resources: list[str] = Field(default_factory=list)
    last_login: datetime | None = None
    login_count: int = 0

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @field_validator("secondary_roles")
    @classmethod
    def secondary_roles_cannot_contain_primary(cls, v: list[UserRole], info):
        if "primary_role" in info.data and info.data["primary_role"] in v:
            raise ValueError("Secondary roles cannot contain the primary role")
        return v


# --- Project Models ---


class TaskDependency(BaseModel):
    # task_# id: str
    dependency_type: Literal["finish_to_start", "start_to_start", "finish_to_finish", "start_to_finish"] = (
        "finish_to_start"
    )
    lag_days: int = 0


class TaskAssignment(BaseModel):
    # user_# id: str
    role: Literal["responsible", "accountable", "consulted", "informed"]
    assigned_at: datetime = Field(default_factory=datetime.now)
    assigned_by: str
    effort_allocation_percent: IntGE1LE100 = 100


class Task(AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: IntGE1LE5 = 3
    estimated_hours: float | None = Field(None, ge=0)
    actual_hours: float | None = Field(None, ge=0)
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    dependencies: list[TaskDependency] = Field(default_factory=list)
    assignments: list[TaskAssignment] = Field(default_factory=list)
    completion_percentage: IntGE0LE100 = 0
    is_milestone: bool = False

    @field_validator("planned_end_date")
    @classmethod
    def end_date_after_start_date(cls, v: date | None, info):
        if (
            v
            and "planned_start_date" in info.data
            and info.data["planned_start_date"]
            and v < info.data["planned_start_date"]
        ):
            raise ValueError("End date must be after start date")
        return v

    @field_validator("actual_end_date")
    @classmethod
    def actual_end_date_validation(cls, v: date | None, info):
        if (
            v
            and "actual_start_date" in info.data
            and info.data["actual_start_date"]
            and v < info.data["actual_start_date"]
        ):
            raise ValueError("Actual end date must be after actual start date")
        return v


class RiskAssessment(BaseModel):
    probability: IntGE1LE5
    impact: IntGE1LE5
    description: str
    mitigation_plan: str | None = None

    @property
    def risk_score(self) -> int:
        return self.probability * self.impact


class ProjectBudget(BaseModel):
    total_amount: MonetaryAmount
    allocated_amounts: dict[str, MonetaryAmount] = Field(default_factory=dict)  # Category -> Amount
    spent_amounts: dict[str, MonetaryAmount] = Field(default_factory=dict)  # Category -> Amount

    @property
    def remaining_budget(self) -> Decimal:
        spent = sum(item.amount for item in self.spent_amounts.values())
        return self.total_amount.amount - spent

    @property
    def budget_utilization_percent(self) -> float:
        if self.total_amount.amount == 0:
            return 0
        spent = sum(item.amount for item in self.spent_amounts.values())
        return float((spent / self.total_amount.amount) * 100)


class Project(TaggedItem, AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: str | None = None
    start_date: date
    target_end_date: date
    actual_end_date: date | None = None
    status: Literal["planning", "active", "on_hold", "completed", "cancelled"] = "planning"
    tasks: list[Task] = Field(default_factory=list)
    # owner_# id: str
    team_members: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    risks: list[RiskAssessment] = Field(default_factory=list)
    budget: ProjectBudget | None = None
    resources: list[str] = Field(default_factory=list)
    priority: IntGE1LE5 = 3
    is_public: bool = False
    # parent_project_  # id: str | None = None

    @field_validator("target_end_date")
    @classmethod
    def target_end_date_after_start_date(cls, v: date, info):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("Target end date must be after start date")
        return v


# --- Event and Incident Models ---


class EventMetadata(BaseModel):
    source: str
    event_type: str
    severity: Literal["debug", "info", "warning", "error", "critical"] = "info"
    correlation_id: str | None = None
    ip_address: IPv4Address | IPv6Address | None = None
    user_agent: str | None = None
    additional_data: dict[str, Any] = Field(default_factory=dict)


class SystemEvent(BaseModel):
    # id: str = Field(default_factory=uuid.str)
    timestamp: datetime = Field(default_factory=datetime.now)
    message: str
    metadata: EventMetadata
    affected_resource_ids: list[str] = Field(default_factory=list)
    affected_user_ids: list[str] = Field(default_factory=list)
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None


class Comment(AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    content: str
    # author_# id: str
    edited: bool = False
    # parent_comment_# id: str | None = None
    mentions: list[str] = Field(default_factory=list)
    attachments: list[AnyUrl] = Field(default_factory=list)


class IncidentTimelineEvent(BaseModel):
    timestamp: datetime
    description: str
    event_type: Literal["detected", "acknowledged", "mitigated", "resolved", "update", "escalated", "workaround"]
    additional_details: str | None = None


class IncidentReport(AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    severity: IncidentSeverity = IncidentSeverity.MINOR
    status: Literal["open", "investigating", "identified", "in_progress", "resolved", "closed"] = "open"
    reported_by: str
    assigned_to: str | None = None
    affected_systems: list[str] = Field(default_factory=list)
    affected_resources: list[str] = Field(default_factory=list)
    affected_users_count: int = 0
    started_at: datetime
    detected_at: datetime
    acknowledged_at: datetime | None = None
    mitigated_at: datetime | None = None
    resolved_at: datetime | None = None
    root_cause: str | None = None
    resolution: str | None = None
    timeline: list[IncidentTimelineEvent] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    linked_events: list[str] = Field(default_factory=list)
    post_mortem_scheduled: bool = False
    post_mortem_completed: bool = False

    @field_validator("detected_at")
    @classmethod
    def detected_not_before_started(cls, v: datetime, info):
        if "started_at" in info.data and v < info.data["started_at"]:
            raise ValueError("Incident cannot be detected before it started")
        return v

    @model_validator(mode='after')
    def check_timeline_consistency(self):
        # This would perform complex validation of the timeline events
        # For example, ensuring resolved comes after mitigated, etc.
        return self


# --- Enterprise System Models ---


class ComplianceFramework(BaseModel):
    name: str
    version: str
    controls: dict[str, dict[str, Any]] = Field(default_factory=dict)
    last_assessment_date: date | None = None
    next_assessment_date: date | None = None
    compliance_score: float | None = Field(None, ge=0, le=100)
    deviations: list[str] = Field(default_factory=list)


class DataRetentionPolicy(BaseModel):
    retention_period_days: int = Field(..., gt=0)
    data_classification: Literal["public", "internal", "confidential", "restricted"]
    archive_after_days: int | None = None
    delete_after_days: int | None = None
    legal_hold: bool = False
    exceptions: list[str] = Field(default_factory=list)


class SystemBackupConfig(BaseModel):
    frequency: Literal["hourly", "daily", "weekly", "monthly"]
    retention_count: int = Field(..., ge=1)
    include_database: bool = True
    include_files: bool = True
    backup_location: str
    encryption_enabled: bool = True
    compression_enabled: bool = True
    last_successful_backup: datetime | None = None
    next_scheduled_backup: datetime | None = None


class SystemConfiguration(BaseModel):
    name: str
    environment: Literal["development", "testing", "staging", "production"]
    version: str
    deployed_at: datetime
    is_active: bool = True
    config_values: dict[str, Any] = Field(default_factory=dict)
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    allowed_ips: list[IPv4Address | IPv6Address | str] = Field(default_factory=list)
    max_concurrent_users: int | None = None
    maintenance_window: dict[str, Any] = Field(default_factory=dict)
    backup_config: SystemBackupConfig | None = None
    compliance_frameworks: list[ComplianceFramework] = Field(default_factory=list)
    data_retention_policies: dict[str, DataRetentionPolicy] = Field(default_factory=dict)


class EnterpriseSystem(AuditInfo):
    # id: str = Field(default_factory=uuid.str)
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    # owner_  # id: str
    status: Literal["planning", "implementing", "operational", "maintenance", "deprecated", "decommissioned"] = (
        "planning"
    )
    criticality: Literal["low", "medium", "high", "critical"] = "medium"
    configuration: SystemConfiguration
    resources: list[Resource] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    incidents: list[IncidentReport] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    administrators: list[str] = Field(default_factory=list)
    users: list[str] = Field(default_factory=list)
    documentation_url: HttpUrl | None = None
    total_cost_of_ownership: MonetaryAmount | None = None
    implemented_date: date | None = None
    last_review_date: date | None = None
    next_review_date: date | None = None
    is_mission_critical: bool = False

    @model_validator(mode='after')
    def check_mission_critical_requirements(self):
        if self.is_mission_critical and self.criticality != "critical":
            raise ValueError("Mission critical systems must have critical criticality")
        return self


# --- Main Complex Example Model ---


class EnterpriseSystemRegistry(BaseModel):
    """
    A comprehensive registry of enterprise systems, users, resources, and incidents.
    This is the top-level model that contains everything.
    """

    organization_name: str
    # organization_  # id: str = Field(default_factory=uuid.str)
    registry_version: str = "1.0.0"
    last_updated: datetime = Field(default_factory=datetime.now)

    # Core registries
    systems: dict[str, EnterpriseSystem] = Field(default_factory=dict)
    projects: dict[str, Project] = Field(default_factory=dict)
    users: dict[str, User] = Field(default_factory=dict)
    resources: dict[str, Resource] = Field(default_factory=dict)
    incidents: dict[str, IncidentReport] = Field(default_factory=dict)
    events: dict[str, SystemEvent] = Field(default_factory=dict)

    # Statistics and metadata
    total_users_count: int = 0
    active_users_count: int = 0
    total_resources_count: int = 0
    total_incidents_count: int = 0
    open_incidents_count: int = 0
    total_cost: MonetaryAmount | None = None

    # Administrative
    global_compliance_frameworks: list[ComplianceFramework] = Field(default_factory=list)
    global_settings: dict[str, Any] = Field(default_factory=dict)
    allowed_authentication_methods: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def update_statistics(self):
        """Update the statistics based on the registry contents"""
        self.total_users_count = len(self.users)
        self.active_users_count = sum(1 for user in self.users.values() if user.is_active)
        self.total_resources_count = len(self.resources)
        self.total_incidents_count = len(self.incidents)
        self.open_incidents_count = sum(
            1 for incident in self.incidents.values() if incident.status not in ["resolved", "closed"]
        )
        return self


def get_complex_schema():
    """Get the complex schema from the EnterpriseSystemRegistry model."""
    return EnterpriseSystemRegistry.model_json_schema()
