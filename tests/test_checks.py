"""Tests for all health checkers."""

from __future__ import annotations

from unittest.mock import MagicMock

from k8s_health_checker.checks.autoscaling import AutoscalingChecker
from k8s_health_checker.checks.nodes import NodeChecker
from k8s_health_checker.checks.pods import PodChecker
from k8s_health_checker.checks.probes import ProbeChecker
from k8s_health_checker.checks.resources import ResourceChecker
from k8s_health_checker.checks.security import SecurityChecker
from k8s_health_checker.checks.workloads import WorkloadChecker
from k8s_health_checker.models import Severity
from tests.conftest import (
    make_deployment,
    make_hpa,
    make_k8s_clients,
    make_node,
    make_pod,
)

# =====================================================================
# Pod Checks
# =====================================================================


class TestPodChecker:
    def test_healthy_pods(self):
        pod = make_pod(phase="Running", restart_count=0)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)

    def test_crash_loop_detected(self):
        pod = make_pod(
            name="crash-pod",
            phase="Running",
            waiting_reason="CrashLoopBackOff",
            restart_count=25,
        )
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert len(critical) >= 1
        assert any("CrashLoopBackOff" in r.name for r in critical)

    def test_pending_pod_detected(self):
        pod = make_pod(name="pending-pod", phase="Pending")
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("Pending" in r.name for r in warnings)

    def test_failed_pod_detected(self):
        pod = make_pod(name="failed-pod", phase="Failed")
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("Failed" in r.name for r in critical)

    def test_oomkilled_detected(self):
        pod = make_pod(
            name="oom-pod",
            phase="Running",
            terminated_reason="OOMKilled",
        )
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("OOMKilled" in r.name for r in critical)

    def test_high_restarts_warning(self):
        pod = make_pod(name="restart-pod", phase="Running", restart_count=8)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = PodChecker(clients).run()
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("restart" in r.name.lower() for r in warnings)


# =====================================================================
# Node Checks
# =====================================================================


class TestNodeChecker:
    def test_healthy_nodes(self):
        node = make_node(ready=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_node.return_value.items = [node]

        results = NodeChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)

    def test_not_ready_detected(self):
        node = make_node(name="bad-node", ready=False)
        clients = make_k8s_clients()
        clients["core_v1"].list_node.return_value.items = [node]

        results = NodeChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("NotReady" in r.name for r in critical)

    def test_disk_pressure_detected(self):
        node = make_node(name="disk-node", disk_pressure=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_node.return_value.items = [node]

        results = NodeChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("DiskPressure" in r.name for r in critical)

    def test_cordoned_node_detected(self):
        node = make_node(name="drain-node", unschedulable=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_node.return_value.items = [node]

        results = NodeChecker(clients).run()
        info = [r for r in results if r.severity == Severity.INFO]
        assert any("cordoned" in r.name.lower() for r in info)


# =====================================================================
# Resource Checks
# =====================================================================


class TestResourceChecker:
    def test_resources_defined(self):
        pod = make_pod(has_requests=True, has_limits=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = ResourceChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)

    def test_missing_requests(self):
        pod = make_pod(has_requests=False, has_limits=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = ResourceChecker(clients).run()
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("requests" in r.name.lower() for r in warnings)


# =====================================================================
# Probe Checks
# =====================================================================


class TestProbeChecker:
    def test_probes_present(self):
        pod = make_pod(has_readiness_probe=True, has_liveness_probe=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = ProbeChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)

    def test_missing_readiness_probe(self):
        pod = make_pod(has_readiness_probe=False, has_liveness_probe=True)
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]

        results = ProbeChecker(clients).run()
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("readiness" in r.name.lower() for r in warnings)


# =====================================================================
# Security Checks
# =====================================================================


class TestSecurityChecker:
    def test_privileged_container_detected(self):
        pod = make_pod(
            namespace="production",
            privileged=True,
        )
        clients = make_k8s_clients()
        clients["core_v1"].list_pod_for_all_namespaces.return_value.items = [pod]
        clients["core_v1"].list_namespaced_pod.return_value.items = [pod]
        # Need namespace list for network policy check
        ns_mock = MagicMock()
        ns_mock.metadata.name = "production"
        clients["core_v1"].list_namespace.return_value.items = [ns_mock]
        clients["networking_v1"].list_namespaced_network_policy.return_value.items = []

        results = SecurityChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert any("rivileged" in r.name for r in critical)


# =====================================================================
# Workload Checks
# =====================================================================


class TestWorkloadChecker:
    def test_healthy_deployment(self):
        dep = make_deployment(replicas=3, ready_replicas=3)
        clients = make_k8s_clients()
        clients["apps_v1"].list_deployment_for_all_namespaces.return_value.items = [dep]
        clients["apps_v1"].list_stateful_set_for_all_namespaces.return_value.items = []
        clients["apps_v1"].list_daemon_set_for_all_namespaces.return_value.items = []

        results = WorkloadChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)

    def test_unhealthy_deployment(self):
        dep = make_deployment(replicas=3, ready_replicas=0, available_replicas=0)
        clients = make_k8s_clients()
        clients["apps_v1"].list_deployment_for_all_namespaces.return_value.items = [dep]
        clients["apps_v1"].list_stateful_set_for_all_namespaces.return_value.items = []
        clients["apps_v1"].list_daemon_set_for_all_namespaces.return_value.items = []

        results = WorkloadChecker(clients).run()
        critical = [r for r in results if r.severity == Severity.CRITICAL]
        assert len(critical) >= 1


# =====================================================================
# Autoscaling Checks
# =====================================================================


class TestAutoscalingChecker:
    def test_hpa_at_max(self):
        hpa = make_hpa(max_replicas=10, current_replicas=10)
        clients = make_k8s_clients()
        autoscaling = clients["autoscaling_v1"]
        autoscaling.list_horizontal_pod_autoscaler_for_all_namespaces.return_value.items = [hpa]

        results = AutoscalingChecker(clients).run()
        warnings = [r for r in results if r.severity == Severity.WARNING]
        assert any("maximum" in r.name.lower() for r in warnings)

    def test_hpa_healthy(self):
        hpa = make_hpa(max_replicas=10, current_replicas=5)
        clients = make_k8s_clients()
        autoscaling = clients["autoscaling_v1"]
        autoscaling.list_horizontal_pod_autoscaler_for_all_namespaces.return_value.items = [hpa]

        results = AutoscalingChecker(clients).run()
        assert any(r.severity == Severity.PASS for r in results)


# =====================================================================
# Model / Score Tests
# =====================================================================


class TestHealthReport:
    def test_perfect_score(self):
        from k8s_health_checker.demo import generate_demo_report

        report = generate_demo_report()
        # Demo report has issues, so score should be less than 100
        assert report.score < 100
        assert report.score >= 0

    def test_grade_assignment(self):
        from datetime import datetime, timezone

        from k8s_health_checker.models import HealthReport

        report = HealthReport(
            cluster_name="test", timestamp=datetime.now(timezone.utc)
        )
        # Empty report = 100 = grade A
        assert report.score == 100
        assert report.grade == "A"

    def test_demo_report_generates(self):
        from k8s_health_checker.demo import generate_demo_report

        report = generate_demo_report()
        assert report.cluster_name == "aks-prod-eastus"
        assert len(report.results) > 0
        assert len(report.critical) > 0
        assert len(report.passed) > 0
