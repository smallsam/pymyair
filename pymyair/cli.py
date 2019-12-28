# -*- coding: utf-8 -*-

"""Console script for pymyair."""

from __future__ import absolute_import

import click
from pymyair.pymyair import MyAir
import json
import requests
import pprint


@click.group(invoke_without_command=True)
@click.argument('ip')
@click.option('--port', default=2025, help='port of MyPlace service')
@click.option(
    '--aircon',
    default="ac1",
    help='aircon id, only required if you have multiple AC units')
@click.pass_context
def cli(ctx, ip, port, aircon):
    """Console script for pymyair."""
    ctx.obj = {}
    if ctx.invoked_subcommand is None:
        click.echo('Add --help for available commands')
    else:
        try:
            ctx.obj['myair'] = MyAir(host=ip, port=port, aircon=aircon)
            ctx.obj['myair'].update()
        except requests.exceptions.ConnectionError:
            raise click.BadParameter(
                "Connection failed, please check IP: %s" %
                (ip))


@cli.command()
@click.pass_context
def on(ctx):
    """turns on AC"""
    ctx.obj['myair'].mode = 'on'


@cli.command()
@click.pass_context
def off(ctx):
    """turns off AC"""
    ctx.obj['myair'].mode = 'off'


@cli.command()
@click.pass_context
def cool(ctx):
    """switches AC to cooling"""
    ctx.obj['myair'].mode = 'cool'


@cli.command()
@click.pass_context
def heat(ctx):
    """switches AC to heating"""
    ctx.obj['myair'].mode = 'heat'


@cli.command()
@click.pass_context
def vent(ctx):
    """switching AC to venting (if available)"""
    ctx.obj['myair'].mode = 'vent'


@cli.command()
@click.pass_context
def dry(ctx):
    """switching AC to drying (if available)"""
    ctx.obj['myair'].mode = 'dry'


@cli.command()
@click.pass_context
def mode(ctx):
    """returns current operating mode"""
    click.echo(ctx.obj['myair'].mode)


@cli.command()
@click.pass_context
def zones(ctx):
    """returns json of zone information"""
    click.echo(json.dumps(ctx.obj['myair'].zones, sort_keys=True, indent=2))


# @cli.command()
# @click.argument('speed')
# @click.pass_context
# def fan(ctx,speed):
#     """sets fan speed"""
#     ctx.obj['myair'].fanspeed = speed

@cli.command()
@click.option('--speed',
              type=click.Choice(['low',
                                 'medium',
                                 'high',
                                 'auto']),
              help='optional, [low|medium|high|auto]')
@click.pass_context
def fan(ctx, speed):
    '''if speed supplied, updates fan speed'''
    if speed:
        ctx.obj['myair'].fanspeed = speed
    else:
        click.echo(ctx.obj['myair'].fanspeed)


def validate_temp_value(ctx, param, value):
    pp = pprint.PrettyPrinter()
    pp.pprint(ctx.params)
    if value not in range(16, 32):  # and ctx.params['value'] in range(0,100):
        raise click.BadParameter(
            'supply settemp or value percentage for zone, not both')
    return value


def validate_zone_set(ctx, param, value):
    if value not in range(1, 10):
        raise click.BadParameter('zone required: [1-10]')
    return value


@cli.command()
@click.option(
    '--zone',
    type=click.IntRange(
        1,
        10),
    callback=validate_zone_set,
    help='zone id as integer [1-10]')
@click.option(
    '--state', type=click.Choice(['on', 'off']), help='optional, [on|off]')
@click.option(
    '--temp',
    type=click.IntRange(
        16,
        32),
    callback=validate_temp_value,
    help='temperature set point as integer in C [16-32]')
@click.option('--value', type=click.IntRange(0, 100),
              help='percentage open as integer [0-100]')
@click.pass_context
def set(ctx, zone, state, value, temp):
    """sets zone parameters

    --temp or --value is required depending on
    whether a temperature sensor is installed
    """
    ctx.obj['myair'].setZone(id=zone, state=state, set_temp=temp, value=value)


@cli.command()
@click.option('--zone', type=click.IntRange(1, 10),
              help='zone id as integer [1-10]')
@click.pass_context
def myzone(ctx, zone):
    '''if zone supplied, updates myZone'''
    if zone in range(1, 10):
        ctx.obj['myair'].myzone = zone
    else:
        click.echo(ctx.obj['myair'].myzone)


if __name__ == '__main__':
    cli(obj={})
