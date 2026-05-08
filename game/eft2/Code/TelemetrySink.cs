using System;
using System.Collections.Generic;
using System.Linq;

public sealed class TelemetrySink : GameObjectSystem<TelemetrySink>
{
	private const int MaxRecentEvents = 12;
	private readonly List<string> _recentEvents = new();
	private int _sequence;

	public IReadOnlyList<string> RecentEvents => _recentEvents;

	public TelemetrySink( Scene scene ) : base( scene )
	{
	}

	public void Emit( string eventName, string eventId, string payload )
	{
		if ( !GameSystem.HasAuthority )
			return;

		_sequence++;

		var line = $"{_sequence:0000} {eventId} {eventName} t={Time.Now:0.00} {payload}";
		_recentEvents.Add( line );

		while ( _recentEvents.Count > MaxRecentEvents )
		{
			_recentEvents.RemoveAt( 0 );
		}

		Log.Info( $"EFT2 telemetry {line}" );
	}

	public string Tail( int count )
	{
		return string.Join( "\n", _recentEvents.TakeLast( count ) );
	}
}
