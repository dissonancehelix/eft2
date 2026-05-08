using System.Linq;

public sealed class Hud : Component
{
	protected override void OnUpdate()
	{
		if ( Scene.Camera is null )
			return;

		var game = GameSystem.Current;
		if ( game is null )
			return;

		var hud = Scene.Camera.Hud;
		var width = Screen.Width;

		hud.DrawRect( new Rect( width * 0.5f - 220.0f, Screen.Height - 92.0f, 440.0f, 58.0f ), Color.Black.WithAlpha( 0.72f ) );
		hud.DrawRect( new Rect( width * 0.5f - 220.0f, Screen.Height - 92.0f, 140.0f, 58.0f ), new Color( 0.8f, 0.04f, 0.03f, 0.78f ) );
		hud.DrawRect( new Rect( width * 0.5f + 80.0f, Screen.Height - 92.0f, 140.0f, 58.0f ), new Color( 0.03f, 0.2f, 0.9f, 0.78f ) );
		hud.DrawText( $"RHINOS {game.red_rhinos_score}", 24.0f, Color.White, new Rect( width * 0.5f - 214.0f, Screen.Height - 82.0f, 132.0f, 40.0f ), TextFlag.Center );
		hud.DrawText( $"{game.blue_bulls_score} BULLS", 24.0f, Color.White, new Rect( width * 0.5f + 84.0f, Screen.Height - 82.0f, 132.0f, 40.0f ), TextFlag.Center );
		hud.DrawText( "EFT2 CORE LOOP", 18.0f, Color.White.WithAlpha( 0.8f ), new Rect( width * 0.5f - 70.0f, Screen.Height - 76.0f, 140.0f, 24.0f ), TextFlag.Center );

		var local = game.Players.FirstOrDefault( p => p.IsValid() && p.Network.Owner == Connection.Local );
		var carrier = game.Ball?.Carrier;
		var carrierText = carrier.IsValid() ? $"{GameSystem.DisplayTeamName( carrier.Team )} carrier: {carrier.DisplayName}" : "Ball loose";
		var localText = local.IsValid()
			? $"You: {GameSystem.DisplayTeamName( local.Team )} speed={local.ChargeSpeed:0} charge={(local.IsCharging ? "yes" : "no")} carrier={(local.IsCarrier ? "yes" : "no")} down={(local.IsKnockedDown ? local.KnockdownRemaining.ToString( "0.0" ) : "no")}"
			: "Waiting for player";

		hud.DrawRect( new Rect( 20.0f, 20.0f, 520.0f, 104.0f ), Color.Black.WithAlpha( 0.62f ) );
		hud.DrawText( carrierText, 20.0f, Color.White, new Vector2( 36.0f, 32.0f ), TextFlag.LeftTop );
		hud.DrawText( localText, 16.0f, Color.White.WithAlpha( 0.82f ), new Vector2( 36.0f, 62.0f ), TextFlag.LeftTop );
		hud.DrawText( $"Players {game.Players.Count} | state {game.RoundState}", 16.0f, Color.White.WithAlpha( 0.72f ), new Vector2( 36.0f, 88.0f ), TextFlag.LeftTop );

		var tail = game.Telemetry?.Tail( 6 );
		if ( !string.IsNullOrWhiteSpace( tail ) )
		{
			hud.DrawRect( new Rect( width - 560.0f, 20.0f, 540.0f, 150.0f ), Color.Black.WithAlpha( 0.58f ) );
			hud.DrawText( tail, 13.0f, Color.White.WithAlpha( 0.76f ), new Vector2( width - 544.0f, 34.0f ), TextFlag.LeftTop );
		}
	}
}
