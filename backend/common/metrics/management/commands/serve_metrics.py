"""
Django management command to serve Prometheus metrics at /metrics
"""

from django.core.management.base import BaseCommand
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.urls import path
from django.conf import settings
from django.core.management import call_command
from django.test import Client


class MetricsView(View):
    """View to serve Prometheus metrics"""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            # Import the registry
            from common.metrics.cache_metrics import _cache_metrics_registry

            # Generate the metrics output
            output = _cache_metrics_registry.generate_latest()

            return HttpResponse(
                output,
                content_type='text/plain; version=0.0.4; charset=utf-8'
            )
        except Exception as e:
            # Fallback if registry fails
            return HttpResponse(
                f"# ERROR: {str(e)}",
                content_type='text/plain'
            )


def metrics_view(request):
    """Alternative metrics view implementation"""
    try:
        from common.metrics.cache_metrics import get_all_cache_stats

        stats = get_all_cache_stats()

        response_lines = [
            "# HELP cache_requests_total Total cache requests",
            "# TYPE cache_requests_total counter",
        ]

        for endpoint, ep_stats in stats['endpoint_stats'].items():
            for status in ['hit', 'miss', 'null_value']:
                response_lines.append(
                    f'cache_requests_total{{endpoint="{endpoint}", status="{status}"}} {ep_stats[status]}'
                )

        response_lines.extend([
            "",
            f"# HELP cache_hit_rate Overall cache hit rate",
            f"# TYPE cache_hit_rate gauge",
            f'cache_hit_rate {stats["hit_rate"]}',
        ])

        return HttpResponse(
            "\n".join(response_lines),
            content_type='text/plain'
        )

    except Exception as e:
        return HttpResponse(
            f"# ERROR: {str(e)}",
            content_type='text/plain'
        )


class Command(BaseCommand):
    help = 'Serve Prometheus metrics for cache monitoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8001,
            help='Port to serve metrics on (default: 8001)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Host to bind to (default: 127.0.0.1)'
        )

    def handle(self, *args, **options):
        import django
        from django.core.management import call_command
        from django.core.management.commands.runserver import Command as RunServerCommand
        from django.conf import settings

        # Update settings to add our metrics URL
        urls = settings.ROOT_URLCONF
        try:
            from django.urls import include
            # Check if metrics_urls already exists
            if not hasattr(settings, 'METRICS_URLS'):
                settings.METRICS_URLS = [
                    path('metrics/', lambda: metrics_view(None)),
                ]
        except ImportError:
            pass

        self.stdout.write(
            self.style.SUCCESS(
                f'Prometheus metrics will be served at: http://{options["host"]}:{options["port"]}/metrics'
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                'Configure your Prometheus to scrape this endpoint every 15 seconds'
            )
        )

        # Start the development server
        from django.core.management.commands.runserver import Command
        command = Command()
        command.use_ipv6 = options['host'] == '::1'
        command.use_threading = True
        command.quiet = options.get('quiet', False)

        # Override the port and host
        command.addrport = f'{options["host"]}:{options["port"]}'

        # Run the server
        command.execute(*args, **options)